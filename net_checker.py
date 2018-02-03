from queue import Queue

from job_executor import JobExecutor
from wrapper_urllib import Request
from threading import Lock

class NetCheckerResults:

    def __init__(self, crawler_result):
        self.crawler_result = crawler_result
        self.num_urls = len(self.crawler_result.urls)
        self.num_urls_queued = 0
        self.num_urls_checked = 0
        self.urls_reached = [False for x in range(self.num_urls)]
        self.full_queue = False
        self.done = False
        self.lock = Lock()

class NetChecker(JobExecutor):

    def __init__(self, options, crawler, max_threads):
        super().__init__(max_threads)
        self.options = options
        self.checked = Queue()
        self.checking = None
        self.url_cache = {}
        self.done = False
        self.start_job(False, self.run_checks, (crawler,))
    
    def run_checks(self, crawler):
        while not crawler.done or not crawler.crawled.empty():
            if self.job_available() and not crawler.crawled.empty():
                if self.checking == None or self.checking.full_queue:
                    self.checking = NetCheckerResults(crawler.crawled.get())
                self.start_job(True, self.check, (self.checking,))
            self.poll_sleep()
        
        while self.jobs_running():
            self.poll_sleep()
        self.done = True

    def check(self, result):
        url = None
        url_idx = -1

        with result.lock:
            result.num_urls_queued += 1
            if result.num_urls_queued == result.num_urls:
                result.full_queue = True
            url_idx = result.num_urls_checked
            url = result.crawler_result.urls[url_idx]
        
        success = False

        if url in self.url_cache:
            success = self.url_cache[url]
        else:
            req = Request(url, self.options.user_agent)
            success = req.success
            self.url_cache[url] = success
        
        with result.lock:
            result.urls_reached[url_idx] = success
            print(url, success)

            result.num_urls_checked += 1
            if result.num_urls_checked == result.num_urls:
                result.done = True
                self.checked.put(result)
        
        self.end_job()
