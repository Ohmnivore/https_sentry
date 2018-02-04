# import sys
# import os
# import time
# import ssl
# import urllib.request

# from options import *

# options = Options()

# def open_file(path):
#     with open(path, 'r', encoding='utf-8') as f:
#         contents = f.read()
#     return contents

# def save_file(path, filestr):
#     with open(path, 'w', encoding='utf-8') as f:
#         f.write(filestr)

# def does_terminate(char):
#     return char == '\n' or char == '\r' or char == ' ' or char == '\'' or char == '"' or char == ')' or char == ']' or char == '<'

# def trim_url(url):
#     if url[len(url) - 1] == '.':
#         return url[:-1]
#     return url

# def reach_found(http_urls, filestr):
#     for http_url in http_urls:
#         target_url = http_url
#         try:
#             if options.do_upgrade:
#                 target_url = http_url.replace(protocol_prefix(options.protocol), protocol_prefix(options.upgrade_protocol))

#             req = urllib.request.Request(
#                 target_url, 
#                 data=None, 
#                 headers={
#                     'User-Agent': options.user_agent
#                 }
#             )
#             urllib.request.urlopen(req)

#             if not options.print_only_errors:
#                 print('  OK ' + target_url)

#             if options.do_upgrade_save:
#                 filestr = filestr.replace(http_url, target_url)

#         except urllib.error.HTTPError as e:
#             print(' ERR ' + target_url + ' -> ' + str(e.getcode()))

#         except urllib.error.URLError as e:
#             print(' ERR ' + target_url + ' -> ' + str(e.reason))

#         except ssl.SSLError as e:
#             print(' ERR ' + target_url + ' -> ' + str(e.reason))
        
#         except ssl.CertificateError as e:
#             print(' ERR ' + target_url + ' -> ' + str(e))
        
#         time.sleep(0.1)

#     return filestr

# def search_contents(filename, filepath, filestr):
#     print(filename)
#     filestr_length = len(filestr)

#     search_str = protocol_prefix(options.protocol)

#     http_urls = []

#     start = 0
#     while start < filestr_length:
#         start = filestr.find(search_str, start)

#         if start < 0:
#             break

#         end_idx = start + len(search_str)
#         while end_idx < filestr_length and not does_terminate(filestr[end_idx]):
#             end_idx += 1
        
#         http_urls.append(trim_url(filestr[start:end_idx]))
#         start = end_idx

#     filestr = reach_found(http_urls, filestr)

#     if options.do_upgrade_save:
#         save_file(filepath, filestr)

#     print('')

# def main():
#     if len(sys.argv) < 3:
#         print('Usage: https_enforcer <files directory> <protocol> <optional: upgrade protocol> <optional: save>')
#         print('')
#         print('Examples:')
#         print('')
#         print(' * https_enforcer _posts http')
#         print('    Will try to reach all found http links')
#         print('')
#         print(' * https_enforcer _posts https')
#         print('    Will try to reach all found https links')
#         print('')
#         print(' * https_enforcer _posts http https')
#         print('    Will find which http links can be upgraded to https')
#         print('')
#         print(' * https_enforcer _posts http https save')
#         print('    Will find which http links can be upgraded to https and replace them in the files')
#         print('')
#         exit(1)

#     global options

#     posts_dir = sys.argv[1]
#     options.protocol = sys.argv[2]

#     if len(sys.argv) > 3:
#         options.upgrade_protocol = sys.argv[3]

#     if len(sys.argv) > 4:
#         options.upgrade_save = sys.argv[4] == 'save'

#     options.do_upgrade = options.upgrade_protocol is not None and options.protocol is not options.upgrade_protocol
#     options.do_upgrade_save = options.do_upgrade and options.do_upgrade_save

#     for root, dirs, files in os.walk(posts_dir, topdown=False):
#         for name in files:
#             path = os.path.join(root, name)
#             search_contents(name, path, open_file(path))

# main()

import sys

from options import Options, ProtocolOptions
from crawler import Crawler
from net_checker import NetChecker
from printer import Printer
import utils

def main():
    argc = len(sys.argv)
    if argc != 2 and argc != 3:
        print('Usage: https_sentry <files directory> <optional: config file>')
        print('')
        print('       If no config file is specified https_sentry will look')
        print('       for "config.yaml" in the current working directory.')
        print('')
        exit(1)

    posts_dir = sys.argv[1]
    config_path = 'config.yaml'
    if argc == 3:
        config_path = sys.argv[2]

    options = Options()
    options.from_yaml(utils.open_file(config_path))

    crawler = Crawler(options, posts_dir, options.crawler_threads)
    net_checker = NetChecker(options, crawler, options.net_checker_threads)
    printer = Printer(options, net_checker, options.printer_threads)

main()
