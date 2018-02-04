from job_executor import JobExecutor

class Printer(JobExecutor):
    def __init__(self, options, net_checker, max_threads):
        super().__init__(max_threads)
        self.options = options
        self.start_job(False, self.run_prints, (net_checker,))

    def run_prints(self, net_checker):
        while not net_checker.done or not net_checker.checked.empty():
            if self.job_available() and not net_checker.checked.empty():
                self.start_job(True, self.print, (net_checker.checked.get(),))
            self.poll_sleep()

    def print(self, result):
        print(result.crawler_result.name)

        for idx in range(result.num_urls):
            url = result.crawler_result.urls[idx]
            success = result.urls_reached[idx]

            if success:
                if not self.options.print_only_errors:
                    print('  OK ' + url)
            else:
                error_description = result.urls_errors[idx]
                to_print = ' ERR ' + url
                if error_description != None:
                    to_print += ' -> ' + error_description
                print(to_print)

        print('')

        self.end_job()
