#!/usr/bin/python

__description__ = "Search url for extra tlds, long subdomains, and ip addresses."
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

"""
Use to identify urls w/ suspicious features. 
"""

import sys
import re
import string
import logging
from collections import Counter


# basic logging for local testing
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='url_analysis.log', filemode='w', level=logging.INFO)

cnt = Counter(urls_cnt=0, extra_tld_cnt=0, ip_cnt=0, long_subs_cnt=0)

tlds = []

# prep tld list
with open('effective_tld_names.dat','r') as tld_list:
    all = tld_list.read().split('\n')
    for line in all:
        # filter out extra newlines and comments
        if line[0:2] not in  ['//','\n','\r','\t','']:
            tlds.append(line)
tld_list.close()

# strip off TLDs from domain
def strip_tlds(dom):
    tld_list = []
    subs = dom.split('.')
    if subs[-1] == 'com':
        subs.remove('com')
        return subs
    subs.reverse()
    for i in range(len(subs)):
        if subs[i] in tlds:
            tld_list.append(subs[i])
        else:
            break
    if tld_list:
        for tld in tld_list:
            subs.remove(tld)
    subs.reverse()
    return subs

# returns true if this is an IP address
def is_ip(list_of_subs):
    result = 0
    for sub in list_of_subs:
        if sub.isdigit():
            result += 1
    return result == 4   
        
def main():
    try:
        with open('urls.txt','r') as f:
            for line in f:
                cnt['urls_cnt'] += 1
                parts = line.split('/')
                domain = parts[2].strip()
                if domain:
                    domain = domain.rstrip(':8080')
                    domain = domain.rstrip(':80')
                    domain_subs = strip_tlds(domain)
                    if is_ip(domain_subs):
                        cnt['ip_cnt'] += 1
                        logging.info('IP found in URL: %s',line.strip())
                    elif 'com' in domain_subs or 'com-' in domain_subs:
                        cnt['extra_tld_cnt'] += 1
                        logging.info('Extra .com found in domain: %s',line.strip())
                    elif len(domain_subs) > 5:
                        cnt['long_subs_cnt'] += 1
                        logging.info('Excessive subdomains found: %s %s','.'.join(domain_subs),line.strip())
            
        f.close()
    
    except Exception as e:
        logging.exception("Error parsing domain: %s",e)
    
    print "# URLS: %d" % cnt['urls_cnt']
    print "# extra subs: %d" % cnt['long_subs_cnt']
    print "# IPs: %d" % cnt['ip_cnt']
    print "# extra tlds: %d" % cnt['extra_tld_cnt']
            

if __name__ == '__main__':
    main()

