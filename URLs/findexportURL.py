#!/usr/bin/env python
# coding=UTF-8

__description__ = "return T/F if URL exists in file"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import os, sys, re, HTMLParser, string

# check utilization
nargs = len(sys.argv)
if nargs != 2:
	print "Usage: %s folder" % os.path.basename(sys.argv[0])
	sys.exit()
else:
	folder_path = sys.argv[1]

# URL regex
URL = re.compile(r'\b(?:https?://|telnet://|gopher://|file://|wais://|ftp://|www\d{0,3}[.])[ ]*(?:[a-zA-Z]|[0-9]|[$-_@.&+=/#~;^:?]|[!*\(\),]|(?:%[0-9a-fA-F]{2}))+\b', re.U)

# includes stored results as {filename:[hits list]}
all = {}

# add/format hits
def addMatch(M,P):
	name = P[68:]
	if name in all:
		curlist = all[name]
		curlist.append(M)
		all[name] = curlist
	else:
		all[name] = [M]

# search given directory for files containing URLs
for root, dirs, files in os.walk(folder_path):
	for file in files:
		path = os.path.join(root, file)
		with open(path, 'rU') as email_file:
			# read all data into single string and strip out strange formatting
			all_text = email_file.read().replace('=\n','').decode('ISO-8859-2')
			# parse html character encodings
			h = HTMLParser.HTMLParser()
			htmlparsed = h.unescape(all_text)

			# grep for URL
			urls = URL.findall(htmlparsed)
			if urls:
				for u in urls:
					addMatch(u, path)
		email_file.close()

# write results to file
with open('C:\\Users\\barracuda\\Desktop\\MALWARE\\EMLs\\test\\URLfiles.txt', 'w') as resultFile:
	for key,value in all.items():
		resultFile.writelines("{0}\t{1}\n".format(key,value))
resultFile.close()
