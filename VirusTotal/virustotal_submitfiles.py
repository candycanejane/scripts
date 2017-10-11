#!/usr/bin/python

__description__ = "Submit file to VirusTotal to scan."
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import os
import json
import requests
import logging
import time
from collections import Counter

"""
Code excerpts provided by VirusTotal:
https://www.virustotal.com/en/documentation/public-api/

VirusTotal API public key limits:
4 requests/minute
5760 requests/day
178560 requests/month

A single batch HTTP request for 10 hashes counts as 10 API requests. Restricted for unique (api key, IP address) tuple.

"""

# VirtualTotal public API key
host = 'www.virustotal.com'
VSAPI = ''

in_folder = '~/Documents/LAB/VirusTotal/ROUND14/'

# basic logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='~/Documents/LAB/VirusTotal/submitfiles12_Feb.log', filemode='w', level=logging.INFO)

cnt = Counter(api_cnt=0, file_cnt=0, error_cnt=0)


# To submit a file to SCAN
def submit(file, filename):
    try:
        params = {'apikey': VSAPI}
        files = {'file': (filename, open(file, 'rb'))}
        response = requests.post('https://www.virustotal.com/vtapi/v2/file/scan', files=files, params=params)
        json_response = response.json()
    
        logging.info("%s submitted. %s", filename, json_response['verbose_msg'])
        cnt['api_cnt'] += 1
    
    except Exception as e:
        logging.exception("Error submitting file %s. Error: %s", filename, e)
        cnt['error_cnt'] += 1


if __name__ == '__main__':
    
    # recurse through files in a directory
    try:
        for root, dirs, files in os.walk(in_folder):
            for file in files:
                file_path = os.path.join(root, file)
                submit(file_path, file)
                logging.info("Submitting %s", file)
                cnt['file_cnt'] += 1
                time.sleep(15)

    except Exception as e:
        logging.exception("Error parsing hash file. %s", e)
        cnt['error_cnt'] += 1
    

    # print stats
    print "total files submitted: %d" % cnt['file_cnt']
    print "total api: %d" % cnt['api_cnt']
    print "# errors: %d" % cnt['error_cnt']