#!/usr/bin/env python
# -*- coding: utf-8 -*-

from queue import Queue, PriorityQueue

from job_executor import JobExecutor
from wrapper_urllib import Request
from threading import Lock

class NetCheckerResult:

    def __init__(self, crawler_result):
        self.crawler_result = crawler_result
        self.num_urls = len(self.crawler_result.urls)
        self.num_urls_queued = 0
        self.num_urls_checked = 0
        self.urls_reached = [False for x in range(self.num_urls)]
        self.urls_errors = [None for x in range(self.num_urls)]
        self.full_queue = False
        self.done = False
        self.lock = Lock()

class NetChecker(JobExecutor):

    def __init__(self, options, crawler, max_threads):
        super().__init__(max_threads)
        self.options = options
        self.checked = PriorityQueue()
        self.checking = None
        self.url_cache = {}
        self.url_success_cache = {}
        self.url_error_cache = {}
        self.done = False
        self.start_job(False, self.run_checks, (crawler,))
    
    def run_checks(self, crawler):
        while not crawler.done or not crawler.crawled.empty():
            if self.job_available() and not crawler.crawled.empty():
                if self.checking == None:
                    self.checking = NetCheckerResult(crawler.crawled.get())
                else:
                    with self.checking.lock:
                        if self.checking.full_queue:
                            self.checking = NetCheckerResult(crawler.crawled.get())
                self.start_job(True, self.check, (self.checking,))
            self.poll_sleep()
        
        while self.jobs_running():
            self.poll_sleep()
        self.done = True

    def check(self, result):
        url = None
        url_idx = -1
        is_new = False
        skipped = False

        with result.lock:
            if result.num_urls == 0:
                result.full_queue = True
                result.done = True
                self.checked.put((result.crawler_result.index, result))
                self.end_job()
                return

            url_idx = result.num_urls_queued
            url = result.crawler_result.urls[url_idx]

            result.num_urls_queued += 1
            if result.num_urls_queued == result.num_urls:
                result.full_queue = True

            if url not in self.url_cache:
                is_new = True
                self.url_cache[url] = True
        
        if is_new:
            req = Request(url, self.options.user_agent, self.options.method)
            with result.lock:
                self.url_success_cache[url] = req.success
                self.url_error_cache[url] = req.error_description
        else:
            skipped = True
            self.skip_job()
            while url not in self.url_success_cache or url not in self.url_error_cache:
                self.poll_sleep()
        
        with result.lock:
            result.num_urls_checked += 1
            if result.num_urls_checked == result.num_urls:
                for idx in range(result.num_urls):
                    url = result.crawler_result.urls[idx]
                    result.urls_reached[idx] = self.url_success_cache[url]
                    result.urls_errors[idx] = self.url_error_cache[url]

                result.done = True
                self.checked.put((result.crawler_result.index, result))
        
        self.end_job(skipped)
