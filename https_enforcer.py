#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Contains the main entry point for https_enforcer"""

import sys
import signal

from job_executor import JobExecutor
from options import Options
from crawler import Crawler
from net_checker import NetChecker
from printer import Printer
import utils


class Shutdown(Exception):
    """This exception is used to react to shutdown signals"""
    pass


def shutdown(_signum, _frame):
    """Handles shutdown signals.

    Raises:
        Shutdown
    """
    raise Shutdown


def main(argv):
    """The application entry point.

    Args:
        argv (list of str): Command line arguments.
    """

    # Print usage if wrong amount of command line arguments
    argc = len(argv)
    if argc != 2 and argc != 3:
        print('Usage: https_sentry <files directory> <optional: config file>')
        print('')
        print('       If no config file is specified https_sentry will look')
        print('       for "config.yaml" in the current working directory.')
        print('')
        exit(1)

    # Parse command line arguments
    posts_dir = argv[1]
    config_path = 'config.yaml'
    if argc == 3:
        config_path = argv[2]

    # Read options from config file
    options = Options()
    options.from_yaml(utils.open_file(config_path))

    # Register signal handlers
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    # Launch our main objects
    crawler = Crawler(options, posts_dir, options.crawler_threads)
    net_checker = NetChecker(options, crawler, options.net_checker_threads)
    printer = Printer(options, net_checker, options.printer_threads)

    # Keep the main thread alive until completion or signal
    # All other threads run in daemon mode and will terminate
    # along with the main thread
    main_job = JobExecutor(0)
    try:
        while not printer.done:
            main_job.poll_sleep()
    except Shutdown:
        pass

if __name__ == '__main__':
    main(sys.argv)
