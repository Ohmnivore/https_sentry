#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread, Lock
import time

class JobExecutor:

    def __init__(self, max_jobs):
        self._num_jobs = 0
        self._max_jobs = max_jobs
        self._offset = 0
        self._lock = Lock()
    
    def start_job(self, in_pool, call, args):
        if in_pool:
            with self._lock:
                self._num_jobs += 1
        Thread(target = call, args = args, daemon = True).start()

    def end_job(self, skipped = False):
        with self._lock:
            self._num_jobs -= 1
            if skipped:
                self._offset -= 1

    def skip_job(self):
        with self._lock:
            self._offset += 1

    def job_available(self):
        with self._lock:
            return self._num_jobs < self._max_jobs + self._offset

    def jobs_running(self):
        with self._lock:
            return self._num_jobs > 0

    def poll_sleep(self, seconds = 0.01):
        time.sleep(seconds)
