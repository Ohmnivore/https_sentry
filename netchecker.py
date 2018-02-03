from threading import Thread

from wrapper_urllib import Request

class NetCheckerResults:

    def __init__(self, crawler_result):
        self.crawler_result = crawler_result
        self.num_urls = len(self.crawler_result.urls)
        self.num_urls_queued = 0
        self.num_urls_checked = 0
        self.urls_reached = [False for x in range(self.num_urls)]
        self.full_queue = False
        self.done = False

class NetChecker:

    def __init__(self, options, crawler_results_queue, max_num_threads):
        self.options = options
        self.num_threads = 0
        self.max_num_threads = max_num_threads
        self.checking = None
        self.url_cache = {}
        Thread(target=self.run_checks, args=(crawler_results_queue,)).start()
    
    def run_checks(self, crawler):
        while not crawler.done or not crawler.crawled.empty():
            if self.num_threads < self.max_num_threads and not crawler.crawled.empty():
                self.num_threads += 1

                if self.checking == None or self.checking.full_queue:
                    self.checking = NetCheckerResults(crawler.crawled.get())
                
                Thread(target=self.check, args=(self.checking,)).start()

    def check(self, result):
        result.num_urls_queued += 1
        if result.num_urls_queued == result.num_urls:
            result.full_queue = True

        url = result.crawler_result.urls[result.num_urls_checked]
        success = False

        if url in self.url_cache:
            success = self.url_cache[url]
        else:
            req = Request(url, self.options.user_agent)
            success = req.success
            self.url_cache[url] = success
        
        result.urls_reached[result.num_urls_checked] = success
        print(url, success)

        result.num_urls_checked += 1
        if result.num_urls_checked == result.num_urls:
            result.done = True
        
        self.num_threads -= 1
