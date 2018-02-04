#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread, Lock
import time

class JobExecutor:

    def __init__(self, max_jobs):
        self.num_jobs = 0
        self.max_jobs = max_jobs
        self.offset = 0
        self.lock = Lock()
    
    def start_job(self, in_pool, call, args):
        if in_pool:
            with self.lock:
                self.num_jobs += 1
        Thread(target = call, args = args, daemon = True).start()

    def end_job(self, skipped = False):
        with self.lock:
            self.num_jobs -= 1
            if skipped:
                self.offset -= 1

    def skip_job(self):
        self.offset += 1

    def job_available(self):
        with self.lock:
            return self.num_jobs < self.max_jobs + self.offset

    def jobs_running(self):
        with self.lock:
            return self.num_jobs > 0

    def poll_sleep(self, seconds = 0.01):
        time.sleep(seconds)
