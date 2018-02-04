#!/usr/bin/env python
# -*- coding: utf-8 -*-

from queue import Queue
import os
import re

from job_executor import JobExecutor
import utils

def does_terminate(char):
    return char == '\n' or char == '\r' or char == ' ' or char == '\'' or char == '"' or char == ')' or char == ']' or char == '<'

def trim_url(url):
    if url[len(url) - 1] == '.':
        return url[:-1]
    return url

class CrawlerResult:

    def __init__(self, index, name, path, urls):
        self.index = index
        self.name = name
        self.path = path
        self.urls = urls

class Crawler(JobExecutor):

    def __init__(self, options, dir, max_threads):
        super().__init__(max_threads)
        self.options = options
        self.crawled = Queue()
        self.files = Queue()
        self.done = False
        self.num_files = 0
        self.num_files_crawled = 0
        # URL-matching regex obtained from https://stackoverflow.com/a/3809435
        self.url_regex = re.compile(self.options.protocol.full + r'(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)')

        # Count files and get their names and paths
        for root, dirs, files in os.walk(dir, topdown=False):
            for name in files:
                self.num_files += 1
                path = os.path.join(root, name)
                self.files.put((name, path))

        self.start_job(False, self.run_crawls, (dir,))

    def run_crawls(self, dir):
        while not self.done:
            if self.job_available() and not self.files.empty():
                index = self.num_files - self.files.qsize()
                name, path = self.files.get()
                self.start_job(True, self.crawl, (index, name, path,))
            self.poll_sleep()

    def crawl(self, index, name, path):
        contents = utils.open_file(path)
        urls = []

        for match in re.finditer(self.url_regex, contents):
            url = match.group()
            url = trim_url(url)
            if self.options.upgrade:
                url = url.replace(self.options.protocol.full, self.options.upgrade_protocol.full)
            urls.append(url)

        result = CrawlerResult(index, name, path, urls)
        self.crawled.put(result)

        self.num_files_crawled += 1
        if self.num_files_crawled == self.num_files:
            self.done = True
        
        self.end_job()
