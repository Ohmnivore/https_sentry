from threading import Thread, Lock
import time

class JobExecutor:

    def __init__(self, max_jobs):
        self.num_jobs = 0
        self.max_jobs = max_jobs
        self.lock = Lock()
    
    def start_job(self, in_pool, call, args):
        if in_pool:
            with self.lock:
                self.num_jobs += 1
        Thread(target=call, args=args).start()

    def end_job(self):
        with self.lock:
            self.num_jobs -= 1

    def job_available(self):
        with self.lock:
            return self.num_jobs < self.max_jobs

    def jobs_running(self):
        with self.lock:
            return self.num_jobs > 0

    def poll_sleep(self, seconds = 0.01):
        time.sleep(seconds)
