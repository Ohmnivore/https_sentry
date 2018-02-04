#!/usr/bin/env python
# -*- coding: utf-8 -*-

from job_executor import JobExecutor
import utils


class Printer(JobExecutor):

    def __init__(self, options, net_checker, max_threads):
        super().__init__(max_threads)
        self._options = options
        self.done = False
        # Used for ordering of results
        self._expected_index = 0
        # Used when replacing URLs in files
        self._extra_chars = self._get_extra_chars()

        self.start_job(False, self._run_prints, (net_checker,))

    def _get_extra_chars(self):
        len_upgrade = len(self._options.upgrade_protocol.protocol)
        len_original = len(self._options.protocol.protocol)
        return len_upgrade - len_original

    def _run_prints(self, net_checker):
        while not net_checker.done or not net_checker.checked.empty():
            if self.job_available() and not net_checker.checked.empty():
                index, result = net_checker.checked.get()
                if index == self._expected_index:
                    self._expected_index += 1
                    self.start_job(True, self._print, (result,))
                else:
                    # Still waiting for the next result according to the
                    # crawler's directory traversal order, so put this
                    # result back into the priority queue.
                    net_checker.checked.put((index, result))
            self.poll_sleep()

        # Wait for active jobs to finish
        while self.jobs_running():
            self.poll_sleep()
        self.done = True

    def _print(self, result):
        # Skip files that had no URLs to check
        if result.num_urls == 0:
            self.end_job()
            return

        print(result.crawler_result.name)

        # Print result for each URL
        for idx in range(result.num_urls):
            url = result.crawler_result.urls[idx].url
            success = result.urls[idx].reached

            if success:
                if not self._options.print_only_errors:
                    print('  OK ' + url)
            else:
                # Report error description, if any
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

        # Offset caused by replacing string with another of a (possibly)
        # different length. URL character indices need to be adjusted by
        # this value.
        offset = 0

        for idx in range(result.num_urls):
            success = result.urls[idx].reached

            if success:
                url = result.crawler_result.urls[idx].url
                start_index = result.crawler_result.urls[idx].start_index
                end_index = result.crawler_result.urls[idx].end_index
                # Adjust index for offset
                start_index += offset
                end_index += offset
                # Update the offset
                offset += self._extra_chars

                # Insert in place of the original URL
                contents = contents[:start_index] + url + contents[end_index:]

        utils.save_file(result.crawler_result.path, contents)
