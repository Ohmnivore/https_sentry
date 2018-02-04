#!/usr/bin/env python
# -*- coding: utf-8 -*-

from job_executor import JobExecutor
import utils


class Printer(JobExecutor):

    def __init__(self, options, net_checker, max_threads):
        super().__init__(max_threads)
        self._options = options
        self.done = False
        self._expected_index = 0
        len_upgrade = len(self._options.upgrade_protocol.protocol)
        len_original = len(self._options.protocol.protocol)
        self._extra_chars = len_upgrade - len_original
        self.start_job(False, self._run_prints, (net_checker,))

    def _run_prints(self, net_checker):
        while not net_checker.done or not net_checker.checked.empty():
            if self.job_available() and not net_checker.checked.empty():
                result = net_checker.checked.get()
                if result[1].crawler_result.index == self._expected_index:
                    self._expected_index += 1
                    self.start_job(True, self._print, (result[1],))
                else:
                    net_checker.checked.put(result)
            self.poll_sleep()

        while self.jobs_running():
            self.poll_sleep()
        self.done = True

    def _print(self, result):
        if result.num_urls == 0:
            self.end_job()
            return

        print(result.crawler_result.name)

        for idx in range(result.num_urls):
            url = result.crawler_result.urls[idx].url
            success = result.urls[idx].reached

            if success:
                if not self._options.print_only_errors:
                    print('  OK ' + url)
            else:
                error_description = result.urls[idx].error_description
                to_print = ' ERR ' + url
                if error_description is not None:
                    to_print += ' -> ' + error_description
                print(to_print)

        print('')

        if self._options.upgrade_save:
            self.replace(result)

        self.end_job()

    def replace(self, result):
        contents = utils.open_file(result.crawler_result.path)
        offset = 0

        for idx in range(result.num_urls):
            src_url = result.crawler_result.urls[idx].src_url
            url = result.crawler_result.urls[idx].url
            index = result.crawler_result.urls[idx].index + offset
            success = result.urls[idx].reached

            if success:
                offset += self._extra_chars
                extract = contents[index:]
                contents = contents[:index] + extract.replace(src_url, url, 1)

        utils.save_file(result.crawler_result.path, contents)
