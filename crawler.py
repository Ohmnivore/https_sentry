from queue import Queue
from threading import Thread
import os

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

    def __init__(self, name, path, urls):
        self.name = name
        self.path = path
        self.urls = urls

class Crawler:

    def __init__(self, options, dir, net):
        self.options = options
        self.crawled = Queue()
        self.done = False
        self.total = 0
        self.progress = 0

        for root, dirs, files in os.walk(dir, topdown=False):
            for name in files:
                self.total += 1
                path = os.path.join(root, name)
                Thread(target=self.search_contents, args=(name, path)).start()
    
    def search_contents(self, name, path):
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
            result = CrawlerResult(name, path, urls)
            self.crawled.put(result)

        self.progress += 1
        if self.progress == self.total:
            self.done = True
