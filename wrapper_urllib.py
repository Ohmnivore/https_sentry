import ssl
import urllib.request
import time

class Request:
    
    def __init__(self, url, user_agent):
        self.success = False
        self.error_description = None
        self.url = url

        try:
            req = urllib.request.Request(
                self.url, 
                data=None, 
                headers={
                    'User-Agent': user_agent
                }
            )
            urllib.request.urlopen(req)
            self.success = True

        except urllib.error.HTTPError as e:
            self.error_description = str(e.getcode())

        except urllib.error.URLError as e:
            self.error_description = str(e.reason)

        except ssl.SSLError as e:
            self.error_description = str(e.reason)
        
        except ssl.CertificateError as e:
            self.error_description = str(e)
