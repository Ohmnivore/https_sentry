#!/usr/bin/env python
# -*- coding: utf-8 -*-

from queue import Queue
import os
import re

from job_executor import JobExecutor
import utils

def trim_url(url):
    """Removes the '.' if it's the last character.

    For cases where the link is the last word in a sentence.
    """
    if url[len(url) - 1] == '.':
        return url[:-1]
    return url

class CrawlerURLResult:

    def __init__(self, src_url, url, index):
        """
        Args:
            src_url (str): The original URL found in the file.
            url (str): The URL with the upgraded protocol. If protocol upgrading is disabled, it's equivalent to src_url.
            index (int): The character index of this URL in the file.
        """
        self.src_url = src_url
        self.url = url
        self.index = index

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
            max_threads (int): The maximum amount of threads to use for crawling.
        """
        super().__init__(max_threads)
        self._options = options
        self.crawled = Queue()
        self._files = Queue()
        self.done = False
        self._num_files = 0
        self._num_files_crawled = 0
        # URL-matching regex obtained from https://stackoverflow.com/a/3809435
        regex = r'(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
        self._url_regex = re.compile(self._options.protocol.full + regex)

        # Count files and get their names and paths
        for root, dummy_dirs, files in os.walk(crawl_dir, topdown=False):
            for name in files:
                self._num_files += 1
                path = os.path.join(root, name)
                self._files.put((name, path))

        self.start_job(False, self._run_crawls, ())

    def _run_crawls(self):
        while not self.done:
            if self.job_available() and not self._files.empty():
                index = self._num_files - self._files.qsize()
                name, path = self._files.get()
                self.start_job(True, self._crawl, (index, name, path,))
            self.poll_sleep()

    def _crawl(self, index, name, path):
        contents = utils.open_file(path)
        urls = []

        for match in re.finditer(self._url_regex, contents):
            url = match.group()
            url = trim_url(url)
            src_url = url
            if self._options.upgrade:
                url = url.replace(self._options.protocol.full, self._options.upgrade_protocol.full)
            urls.append(CrawlerURLResult(src_url, url, match.start()))

        result = CrawlerResult(index, name, path, urls)
        self.crawled.put(result)

        self._num_files_crawled += 1
        if self._num_files_crawled == self._num_files:
            self.done = True

        self.end_job()
