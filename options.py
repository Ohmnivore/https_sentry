#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml

class ProtocolOptions:

    def __init__(self, protocol):
        self.protocol = protocol
        self.full = protocol + '://'

class Options:
    
    def __init__(self):
        # Protocols
        self.protocol = None
        self.upgrade_protocol = None

        # Upgrading
        self.upgrade = False
        self.upgrade_save = False

        # Output
        self.print_only_errors = False

        # HTTP config
        self.user_agent = None
        self.method = None

        # Threads
        self.crawler_threads = -1
        self.net_checker_threads = -1
        self.printer_threads = -1

    def from_yaml(self, contents):
        cfg = yaml.load(contents)

        # Protocols
        self.protocol = ProtocolOptions(cfg['protocol'])
        self.upgrade_protocol = ProtocolOptions(cfg['upgrade_protocol'])

        # Upgrading
        self.upgrade = cfg['upgrade']
        self.upgrade_save = cfg['upgrade_save']

        # Output
        self.print_only_errors = cfg['print_only_errors']

        # HTTP config
        self.user_agent = cfg['user_agent']
        self.method = cfg['method']

        # Threads
        self.crawler_threads = cfg['crawler_threads']
        self.net_checker_threads = cfg['net_checker_threads']
        self.printer_threads = cfg['printer_threads']

        # Validation
        if self.protocol.protocol == self.upgrade_protocol.protocol:
            self.upgrade = False
            self.upgrade_save = False
        
        if not self.upgrade:
            self.upgrade_save = False
