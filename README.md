# Purpose
This is a Python 3 console application for checking the status of all the URLs of a static Jekyll site.

The primary use-cases are:
* Identifying dead links (the resource may have moved or disappeared after a post was written)
* Identifying which links can be upgraded from **HTTP** to **HTTPS** (the host may have acquired **HTTPS** support after a post was written)

These checks come in handy for general blog maintenance.

# Usage
Run the `https_sentry.py` script with arguments as described:
```
Usage: https_sentry <files directory> <optional: config file>

       If no config file is specified https_sentry will look
       for "config.yaml" in the current working directory.
```

# Features
* Multi-threading for file reads and link searches, network requests, and file writes
* URL cache to prevent duplicate network requests
* Flexible configuration

# Dependencies
* Python 3
* PyYAML

# Configuration
This is a sample `config.yaml` file:
```
# Protocols ###################################################################
# The protocol of the links to search for
protocol: http
# The protocol to use instead for the found links
upgrade_protocol: https

# Upgrading ###################################################################
# Whether to perform the protocol substitution
upgrade: False
# Whether to write the changes to disk for the successfully reached links
# Setting this to false will ensure a 'dry run'
upgrade_save: False

# Output ######################################################################
print_only_errors: False

# HTTP config #################################################################
user_agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0
# HEAD will make the server send only the header (saving time and bandwidth),
# while a response to GET will also include the body
method: HEAD

# URL regex ###################################################################
# The regex used to match URLs, without the protocol prefix (no http(s)://)
# https_sentry will prepend the appropriate prefix during the crawl
# This URL-matching regex was obtained from https://stackoverflow.com/a/3809435
url_regex: (www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)

# Threads #####################################################################
# Reads files and finds the links
crawler_threads: 4
# Checks the links - this is usually the bottleneck
net_checker_threads: 16
# Prints output and saves the files (if upgrade_save is True)
printer_threads: 4

```

# Common configurations
### Check all **HTTP** links
* Set `protocol` to `http`
* Set `upgrade` to `False`

### Check all **HTTPS** links
* Set `protocol` to `https`
* Set `upgrade` to `False`

### Check which **HTTP** links can be upgraded to **HTTPS**
* Set `protocol` to `http`
* Set `upgrade_protocol` to `https`
* Set `upgrade` to `True`

### Check which **HTTP** links can be upgraded to **HTTPS**, and replace the ones that can in the files
* Set `protocol` to `http`
* Set `upgrade_protocol` to `https`
* Set `upgrade` to `True`
* Set `upgrade_save` to `True`

# TODO
* Better docstrings
* Handle incomplete config file
* Better config file validation
* Automated tests
