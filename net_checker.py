#!/usr/bin/env python
# -*- coding: utf-8 -*-

from queue import Queue, PriorityQueue

from job_executor import JobExecutor
from wrapper_urllib import Request
from threading import Lock


class NetCheckerURLResult:

    def __init__(self):
        self.reached = False
        self.error_description = None


class NetCheckerResult:

    def __init__(self, crawler_result):
        self.crawler_result = crawler_result
        self.num_urls = len(self.crawler_result.urls)
        self.num_urls_queued = 0
        self.num_urls_checked = 0
        self.urls = [NetCheckerURLResult() for x in range(self.num_urls)]
        self.full_queue = False
        self.done = False
        self.lock = Lock()

    def add_queued(self):
        self.num_urls_queued += 1
        if self.num_urls_queued == self.num_urls:
            self.full_queue = True

    def add_checked(self):
        self.num_urls_checked += 1
        if self.num_urls_checked == self.num_urls:
            self.done = True


class NetChecker(JobExecutor):

    def __init__(self, options, crawler, max_threads):
        super().__init__(max_threads)
        self._options = options
        self.checked = PriorityQueue()
        self._checking = None
        self._url_cache = {}
        self._url_success_cache = {}
        self._url_error_cache = {}
        self.done = False
        self.start_job(False, self._run_checks, (crawler,))

    def _run_checks(self, crawler):
        while not crawler.done or not crawler.crawled.empty():
            if self.job_available():
                if self._checking is None:
                    if crawler.crawled.empty():
                        # Crawler hasn't produced any results at all yet
                        self.poll_sleep()
                        continue
                    else:
                        # This is the first result the crawler has produced
                        self._checking = NetCheckerResult(crawler.crawled.get())
                else:
                    if (self._checking.full_queue and
                            not crawler.crawled.empty()):
                        # The current result is fully scheduled, start working
                        # on the next one
                        self._checking = NetCheckerResult(crawler.crawled.get())
                # Check one URL from the current crawler result
                self.start_job(True, self._check, (self._checking,))
            self.poll_sleep()

        # Fully schedule the last crawler result
        while self._checking is not None and not self._checking.full_queue:
            if self.job_available():
                self.start_job(True, self._check, (self._checking,))
            self.poll_sleep()

        # Wait for active jobs to finish
        while self.jobs_running():
            self.poll_sleep()
        self.done = True

    def _check(self, result):
        url = None
        url_idx = -1
        is_new = False
        skipped = False

        with result.lock:
            # Skip results with no URLs
            if result.num_urls == 0:
                result.full_queue = True
                result.done = True
                self.checked.put((result.crawler_result.index, result))
                self.end_job()
                return

            # Get URL
            url_idx = result.num_urls_queued
            url = result.crawler_result.urls[url_idx].url
            result.add_queued()

            # Check if the URL is already checked or in the process of being
            # checked
            if url not in self._url_cache:
                is_new = True
                # Set as being checked in cache
                self._url_cache[url] = True

        # URL not in cache
        if is_new:
            # Send a request, block the thread while the resource is unlocked
            req = Request(url, self._options.user_agent, self._options.method)
            with result.lock:
                # Lock resource and write results
                self._url_success_cache[url] = req.success
                self._url_error_cache[url] = req.error_description
        # URL already in cache
        else:
            # Allow another thread to be spun up, as this one will not perform
            # a network request
            skipped = True
            self.skip_job()
            while (url not in self._url_success_cache or
                   url not in self._url_error_cache):
                # If the URL is in the process of being checked, wait for it
                # to finish and for the results to become available
                self.poll_sleep()

        with result.lock:
            result.add_checked()
            if result.done:
                self._finalize_result(result)

        self.end_job(skipped)

    def _finalize_result(self, result):
        # Copy the cache contents for each URL
        for idx in range(result.num_urls):
            url = result.crawler_result.urls[idx].url
            result.urls[idx].reached = self._url_success_cache[url]
            result.urls[idx].error_description = self._url_error_cache[url]

        self.checked.put((result.crawler_result.index, result))
