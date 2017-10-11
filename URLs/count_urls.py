#!/usr/bin/python

__description__ = "Counts filetypes from list of URLs."
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"
__version__ = 1.0

import sys
import os
import re
import logging
from collections import Counter

# basic logging for local testing
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='~/Documents/LAB/URL/countdownloads.txt', filemode='w', level=logging.INFO)


# aggregate stats for folder (sorted by month)
cnt = Counter(office_cnt=0, download_cnt=0)

# regex for getting the domain
DOMAIN = re.compile(r'https?:\/\/([\w\d\.:-]*)\/')

def count_office(file):
    try:
        with open(file, 'r') as f:
            text = f.read()
            lines = text.split('\n')
            for line in lines:
                (fname, ext) = os.path.splitext(line.lower())
                if ext in ['.doc', '.docx', '.docm', '.dot', '.dotx', '.dotm', '.xls', '.xlsb', '.xlsx', '.xlsm', '.xla', '.xlam', '.xlt', '.xltx', '.xltm', '.xlm', '.ppt', '.pptm', '.pptx', '.pot', '.potm', '.potx', '.ppa', '.ppam', '.pps', '.ppsm', '.ppsx']:
                    cnt['office_cnt'] += 1
                    logging.info(line)
        f.close()
    except Exception as e:
        logging.exception('Error parsing line.')

def count_download(file):
    try:
        with open(file, 'r') as f:
            text = f.read()
            lines = text.split('\n')
            for line in lines:
                domain_hit = DOMAIN.search(line)
                if domain_hit:
                    domain = domain_hit.group(1)
                    if domain in ['drive.google.com','www.dropbox.com','docs.google.com','onedrive.live.com', 'mega.nz', 'www105.zippyshare.com', 'www.mediafire.com','www.hightail.com','www.sendspace.com','s000.tinyupload.com','ufile.io','uploadfiles.io','7minutestothetop.com','ul.to','www.icloud.com']:
                        cnt['download_cnt'] += 1
                        logging.info(line)
        f.close()
    except Exception as e:
        logging.exception('Error parsing line.')

if __name__ == '__main__':
    # check utilization
    nargs = len(sys.argv)
    if nargs != 2:
        print "Usage: {0} file".format(os.path.basename(sys.argv[0]))
        sys.exit()
    else:
        file_path = sys.argv[1]
        if not os.path.isfile(file_path):
            logging.error("File does not exist: %s", file_path)
            sys.exit()

        
        # Count links to Office documents
        #count_office(file_path)
        #print "Total: %s" % cnt['office_cnt']
        
        # Count links to downloads
        count_download(file_path)
        print "Total: %s" % cnt['download_cnt']