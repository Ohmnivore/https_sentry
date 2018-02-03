class ProtocolOptions:

    def __init__(self, protocol):
        self.protocol = protocol
        self.full = protocol + '://'

class Options:
    
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'
        self.protocol = None
        self.upgrade_protocol = None
        self.upgrade_save = False
        self.print_only_errors = False
        self.do_upgrade = False
        self.do_upgrade_save = False
