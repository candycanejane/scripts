#!/usr/bin/python

__description__ = "Count hits from VS json files."
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import sys
import os
import logging
import json

# basic logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='~/Documents/LAB/VirusTotal/counthits_jan.log', filemode='w', level=logging.INFO)


hits = {}
hits2 = []

def parse_json(json_dict):
    scans = json_dict.get('scans',{})
    # pull out vendor results
    for vend in scans:
        # if vendor detected, pull out specific signature
        if scans.get(vend,{}).get('detected') == True:
            hit = vend+": "+scans.get(vend,{}).get('result')
            if hit in hits:
                # increase count
                hits[hit] += 1
            else:
                # initialize new signature
                hits[hit] = 1


def parse_files(folder_path):
    # recurse through directory
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r') as f:
                    text = f.read()
                    json_dict = json.loads(text)
                    parse_json(json_dict)
                f.close()
            except Exception as e:
                logging.exception("Error parsing file %s: %s", file, e)
    
# main logic to parse folder of json files w/ VirusTotal results and generate stats
def main(argv):
    # check utilization
    nargs = len(argv)
    if nargs != 2:
        print "Usage: {0} in_folder".format(os.path.basename(argv[0]))
        sys.exit()
    else:
        in_folder = argv[1]

        if not os.path.isdir(in_folder):
            logging.error("Input folder does not exist.")
            sys.exit()
        
        try:
            parse_files(in_folder)
        
            for keys,values in hits.items():
                s = "{0}: {1}".format(keys,values)
                hits2.append(s)
            
            s_hits = sorted(hits2)
            
            logging.info("\n".join(s_hits))
        
        except Exception as e:
            logging.exception("Error: %s", e)
        

if __name__ == '__main__':
    main(sys.argv)