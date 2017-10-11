#!/usr/bin/python

__description__ = "Pull past VirusTotal reports from list of hashes."
__author__ = "candycanjane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import os
import sys
import logging
from shutil import copy

in_folder = '~/Documents/LAB/VirusTotal/VS/'
out_folder = '~/Documents/LAB/VirusTotal/VS_Feb/'


# basic logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='~/Documents/LAB/VirusTotal/searchVSFeb.log', filemode='w', level=logging.INFO)

def checkHash(hash):
    # recurse through files in a VirusTotal directory; copy if there's a matching json file
    try:
        for root, dirs, files in os.walk(in_folder):
            for file in files:
                fname, ext = os.path.splitext(file)
                fname2 = fname.strip()
                if fname2 == hash and ext == ".json":
                    file_path = os.path.join(root, file)
                    try:
                        logging.info("Copying: %s", fname2+".json")
                        copy(file_path, out_folder+fname2+".json")
                    except Exception as e:
                        logging.exception("Error copying file: %s", e)
    except Exception as e:
        logging.exception("Error comparing hash: %s Error: %s", hash, e)


if __name__ == '__main__':

    # recurse through files in a directory
    try:
        with open('~/Documents/LAB/VirusTotal/round13hashes_Feb.txt', 'r') as file:
            for line in file:
                hash = line.strip()
                logging.info("Checking hash: %s", hash)
                checkHash(hash)
        file.close()
    except Exception as e:
        logging.exception("Error: %s", e)