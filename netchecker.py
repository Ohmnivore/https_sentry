from threading import Thread

from wrapper_urllib import Request

class NetCheckerResults:

    def __init__(self, crawler_result):
        self.crawler_result = crawler_result
        self.num_urls = len(self.crawler_result.urls)
        self.num_urls_checked = 0
        self.urls_reached = [False for x in range(self.num_urls)]
        self.done = False

class NetChecker:

    def __init__(self, options, crawler_results_queue, max_num_threads):
        self.options = options
        self.num_threads = 0
        self.max_num_threads = max_num_threads
        self.checking = None
        Thread(target=self.run_checks, args=(crawler_results_queue,)).start()
    
    def run_checks(self, crawler):
        while not crawler.done:
            if self.num_threads < self.max_num_threads and not crawler.crawled.empty():
                self.num_threads += 1

                if self.checking == None or self.checking.done:
                    self.checking = NetCheckerResults(crawler.crawled.get())
                
                Thread(target=self.check, args=(self.checking,)).start()

    def check(self, result):
        url = result.crawler_result.urls[result.num_urls_checked]
        req = Request(url, self.options.user_agent)

        if req.success:
            result.urls_reached[result.num_urls_checked] = True
        
        print(url, req.success)

        result.num_urls_checked += 1
        if result.num_urls_checked == result.num_urls:
            result.done = True
        
        self.num_threads -= 1
