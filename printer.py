#!/usr/bin/env python
# -*- coding: utf-8 -*-

from job_executor import JobExecutor

class Printer(JobExecutor):
    def __init__(self, options, net_checker, max_threads):
        super().__init__(max_threads)
        self.options = options
        self.done = False
        self.expected_index = 0
        self.start_job(False, self.run_prints, (net_checker,))

    def run_prints(self, net_checker):
        while not net_checker.done or not net_checker.checked.empty():
            if self.job_available() and not net_checker.checked.empty():
                result = net_checker.checked.get()
                if result[1].crawler_result.index == self.expected_index:
                    self.expected_index += 1
                    self.start_job(True, self.print, (result[1],))
                else:
                    net_checker.checked.put(result)
            self.poll_sleep()
        
        while self.jobs_running():
            self.poll_sleep()
        self.done = True

    def print(self, result):
        if result.num_urls == 0:
            self.end_job()
            return

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
