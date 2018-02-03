from queue import Queue
import os

from job_executor import JobExecutor

def open_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        contents = f.read()
    return contents

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
        contents = open_file(path)

        contents_length = len(contents)
        search_str = self.options.protocol.full

        urls = []

        start = 0
        while start < contents_length:
            start = contents.find(search_str, start)

            if start < 0:
                break

            end_idx = start + len(search_str)
            while end_idx < contents_length and not does_terminate(contents[end_idx]):
                end_idx += 1
            
            url = trim_url(contents[start:end_idx])
            if self.options.do_upgrade:
                url = url.replace(self.options.protocol.full, self.options.upgrade_protocol.full)
            urls.append(url)

            start = end_idx

        if len(urls) > 0:
            result = CrawlerResult(index, name, path, urls)
            self.crawled.put(result)

        self.num_files_crawled += 1
        if self.num_files_crawled == self.num_files:
            self.done = True
        
        self.end_job()
