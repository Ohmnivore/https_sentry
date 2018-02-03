from threading import Thread
import time

class JobExecutor:

    def __init__(self, max_jobs):
        self.num_jobs = 0
        self.max_jobs = max_jobs
    
    def start_job(self, in_pool, call, args):
        if in_pool:
            self.num_jobs += 1
        Thread(target=call, args=args).start()

    def end_job(self):
        self.num_jobs -= 1

    def job_available(self):
        return self.num_jobs < self.max_jobs

    def jobs_running(self):
        return self.num_jobs > 0

    def poll_sleep(self, seconds = 0.01):
        time.sleep(seconds)
