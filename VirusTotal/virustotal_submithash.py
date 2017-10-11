#!/usr/bin/python

__description__ = "Submit batch hashes to VirusTotal and parse report."
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import os
import json as JSON
import urllib
import urllib2
import requests
import logging
import time
from shutil import copy
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

# VirtualTotal public API key (get your own)
host = 'www.virustotal.com'
VSAPI = ''

out_folder = '~/Documents/LAB/VirusTotal/VS_Feb'

# basic logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='~/Documents/LAB/VirusTotal/virustotal_Feb2.log', filemode='w', level=logging.INFO)

cnt = Counter(api_cnt=0, file_cnt=0, error_cnt=0, mal_cnt=0, clean_cnt=0)


# HTTP 204 means we've exceeded the public API rate limit
# HTTP Error 403 Forbidden means we don't have privileges for the requested info 
def parseReport(json_dict):
	"""
	Sample response_dict:

	{u'scan_id': u'24b357ee7ef30015c1167540322759ed3c20cb418247aafbaa21f74872af1161-1455786711', 
	u'sha1': u'2c36f226de24191277001246dba646f59c05b715', 
	u'resource': u'24b357ee7ef30015c1167540322759ed3c20cb418247aafbaa21f74872af1161', 
	u'response_code': 1, 
	u'scan_date': u'2016-02-18 09:11:51', 
	u'permalink': u'https://www.virustotal.com/file/24b357ee7ef30015c1167540322759ed3c20cb418247aafbaa21f74872af1161/analysis/1455786711/', 
	u'verbose_msg': u'Scan finished, information embedded', 
	u'sha256': u'24b357ee7ef30015c1167540322759ed3c20cb418247aafbaa21f74872af1161', 
	u'positives': 32, 
	u'total': 55, 
	u'md5': u'46ec763b86a40921f8acb8a47303e5c7', 
	u'scans': 
		{u'Bkav': 
			{u'detected': False, u'version': u'1.3.0.7400', u'result': None, u'update': u'20160217'}, 
		u'MicroWorld-eScan': 
			{u'detected': True, u'version': u'12.0.250.0', u'result': u'X97M.Downloader.BF', u'update': u'20160218'}}}

	"""
	scans = json_dict.get('scans',{})
	# pull out vendor results
	results = []
	for vend in scans:
		# if vendor detected, pull out specific signature
		if scans.get(vend,{}).get('detected') == True:
			results.append("{0}:{1}".format(vend,scans.get(vend,{}).get('result')))
	# report clean vs. malicious 
	if results:
		out = ','.join(results)
		logging.info("%s,%d,%s", json_dict['sha256'], json_dict['positives'], out)
		cnt['mal_cnt'] += 1
	else:
		logging.info("%s,No hits", json_dict['sha256'])
		cnt['clean_cnt'] += 1


# Get a file report by MD5/SHA1/SHA256 or scan_id
"""
Use marshal module to write json results dictionary to Python 2.7 datafile for easy loading later (remembers dictionary format). We export plain text file too.
To reload .dat file:
in = open('file.dat', 'rb')
json = marshal.load(in)
in.close()

"""
def getReport(hash):
	url = 'https://www.virustotal.com/vtapi/v2/file/report'

	# Process single hash at a time for now
	parameters = {'resource': hash, 'apikey': VSAPI}
	cnt['api_cnt'] += 1

	#logging.info("Processing request for: %s",hash)
	try:
		data = urllib.urlencode(parameters)
		req = urllib2.Request(url, data)
		response = urllib2.urlopen(req)
		json = response.read()
	except urllib2.URLError as e:
		logging.exception("Error making URL request. Reason:%s Error:%s", e.reason, e)
		cnt['error_cnt'] += 1
		return
	except urllib2.HTTPError as e:
		logging.exception("HTTP Error. Code:%s Reason:%s Error:%s", e.code, e.reason, e)
		cnt['error_cnt'] += 1
		return

	try:
		json_dict = JSON.loads(json)
	except ValueError as e:
		print json 
		logging.exception("Error parsing JSON. Error: %s", e)
		cnt['error_cnt'] += 1
		return
		
	try:
		# write raw results to txt file
		fname = hash.strip()
		path = os.path.join(out_folder, "{0}.json".format(fname))
		with open(path, 'w') as f:
			f.write(json)
		f.close()

	except Exception as e:
		logging.exception("Error writing out json for %s. %s", hash, e)
		cnt['error_cnt'] += 1

	# Parse result - check error codes and log appropriately
	if json_dict['response_code'] == 0:
	    logging.info("Not found. %s %s", hash, json_dict['verbose_msg'])
	elif json_dict['response_code'] == 1:
		#parse json report
		parseReport(json_dict)
	elif json_dict['response_code'] == -2:
		logging.info("Report still processing. %s %s", hash, json_dict['verbose_msg'])
	else:
		logging.error("Some error. Code: %d Error: %s", json_dict['response_code'], json_dict['verbose_msg'])
		cnt['error_cnt'] += 1


if __name__ == '__main__':
	
	# parse through text file of hashes to be submitted
	try:
		with open('~/Documents/LAB/VirusTotal/notfound_Feb.txt', 'r') as file:
			for line in file:
				getReport(line)
				cnt['file_cnt'] += 1
				time.sleep(15)
		file.close()
		    
	except Exception as e:
		logging.exception("Error parsing hash file. %s", e)
		cnt['error_cnt'] += 1

	# print stats
	print "total hashes submitted: %d" % cnt['file_cnt']
	print "total api: %d" % cnt['api_cnt']
	print "# malicious: %d" % cnt['mal_cnt']
	print "# clean: %d" % cnt['clean_cnt']
	print "# unknown: %d" % cnt['unk_cnt']
	print "# errors: %d" % cnt['error_cnt']