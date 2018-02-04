#!/usr/bin/env python
# -*- coding: utf-8 -*-

from queue import Queue
import os
import re

from job_executor import JobExecutor
import utils


def trim_url(url):
    """Removes '.' if it's the last character.

    For cases where the link is the last word in a sentence.
    """
    if url[len(url) - 1] == '.':
        return url[:-1]
    return url


class CrawlerURLResult:

    def __init__(self, src_url, url, start_index, end_index):
        """
        Args:
            src_url (str): The original URL found in the file.
            url (str): The URL with the upgraded protocol. If protocol
                upgrading is disabled, it's equivalent to src_url.
            start_index (int): The index of the first character of this URL in
                the file.
            end_index (int): The index of the last character + 1 of this URL
                in the file.
        """
        self.src_url = src_url
        self.url = url
        self.start_index = start_index
        self.end_index = end_index


class CrawlerResult:

    def __init__(self, index, name, path, urls):
        """
        Args:
            index (int): This file's position in the directory traversal order.
            name (str): The filename.
            path (str): The filepath.
            urls (list of CrawlerURLResult): The found URLs.
        """
        self.index = index
        self.name = name
        self.path = path
        self.urls = urls


class Crawler(JobExecutor):

    def __init__(self, options, crawl_dir, max_threads):
        """
        Args:
            options (Options): The global configuration.
            crawl_dir (str): The directory to crawl through.
            max_threads (int): The maximum amount of threads to use for
                crawling.
        """
        super().__init__(max_threads)
        self._options = options
        self.crawled = Queue()
        self._files = Queue()
        self.done = False
        self._num_files = 0
        self._url_regex = re.compile(options.protocol.full + options.url_regex)

        self._gather_files(crawl_dir)
        self.start_job(False, self._run_crawls, ())

    def _gather_files(self, crawl_dir):
        # Count files and get their names and paths
        for root, dummy_dirs, files in os.walk(crawl_dir, topdown=False):
            for name in files:
                self._num_files += 1
                path = os.path.join(root, name)
                self._files.put((name, path))

    def _run_crawls(self):
        while not self._files.empty():
            if self.job_available():
                index = self._num_files - self._files.qsize()
                name, path = self._files.get()
                self.start_job(True, self._crawl, (index, name, path,))
            self.poll_sleep()

        self.done = True

    def _crawl(self, index, name, path):
        contents = utils.open_file(path)
        urls = []

        for match in re.finditer(self._url_regex, contents):
            url = match.group()
            url = trim_url(url)
            src_url = url
            url = self._upgrade_url(url)
            urls.append(
                CrawlerURLResult(
                    src_url,
                    url,
                    match.start(),
                    match.end()
                )
            )

        result = CrawlerResult(index, name, path, urls)
        self.crawled.put(result)

        self.end_job()

    def _upgrade_url(self, url):
        if self._options.upgrade:
            return url.replace(
                self._options.protocol.full,
                self._options.upgrade_protocol.full
            )
        else:
            return url
