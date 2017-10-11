#!/usr/bin/env python
# coding=UTF-8

__description__ = "copy file to given location if URL exists in file"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import os, sys, re, HTMLParser, string
from shutil import copy

# check utilization
nargs = len(sys.argv)
if nargs != 3:
	print "Usage: %s inFolder outFolder" % os.path.basename(sys.argv[0])
	sys.exit()
else:
	srcDir = sys.argv[1]
	destDir = sys.argv[2]

# URL regex
URL = re.compile(r'\b(?:https?://|telnet://|gopher://|file://|wais://|ftp://|www\d{0,3}[.])[ ]*(?:[a-zA-Z]|[0-9]|[$-_@.&+=/#~;^:?]|[!*\(\),]|(?:%[0-9a-fA-F]{2}))+\b', re.U)

# match email text to regex expression
def containsURL(filename):
	with open(filename, 'rU') as email_file:
		print "working on %s" % filename 
		# read all data into single string and strip out strange formatting
		print "read all text"
		all_text = email_file.read().replace('=\n','').decode('ISO-8859-2')
		# parse html character encodings
		h = HTMLParser.HTMLParser()
		print "parsing html"
		htmlparsed = h.unescape(all_text)

		# grep for URL
		print "searching for URLs"
		urls = URL.findall(htmlparsed)
		print "T/F logic"
		# if file contains URLs, return True 
		if urls:
			return True
		else:
			return False 
		email_file.close()

# iterate over files in folder and copies if they contain a URL 
for filename in os.listdir(srcDir):
	path = os.path.join(srcDir, filename)
	if not os.path.isfile(path):
		continue
	elif containsURL(path):
		print "Copying %s" % path
		copy(path, destDir)
	else:
		print "No links..passing"
		continue

