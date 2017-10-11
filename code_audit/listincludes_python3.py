#!/usr/bin/python

__description__ = "Build a dictionary containing list of files and their include/referenced files"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import sys, os, string, re
from io import BufferedIOBase

"""
Script to identify unused code (old files that are no longer referenced) in large web application

"""

# check usage
nargs = len(sys.argv)
if nargs != 3:
	print("Usage: %s in_folder out_file".format(os.path.basename(sys.argv[0])))
	sys.exit()
else:
	inputFolder = sys.argv[1]
	outputFile = sys.argv[2]

# includes stored as {file:[includes list]}
all = {}

# list of filenames
listoffiles = []

# URL regex
inc = re.compile(r'\b(?<!\/\/)(?:require|require_once|include|include_once|sprintf|header)(?:[\s\(]+[\'"])([\w:/.\s]*(?:\.php|\.inc))(?=[?\'\"])', re.U)
nav = re.compile(r'\b(?:array\(|printNavigation\(|define\()[\w\s",\$\/\']*[\'"\/]([\w:/.\s]*(?:\.php|\.inc))(?=[?\'\"])', re.U)
js = re.compile(r'\b(?:action=|src=|href=)["\\\/]+([\w:/.\s]*(?:\.php|\.inc|\.css|\.js))(?=[?\'\"])', re.U)

# only include html, inc, sh, php, js, and css files in search
def include(path):
	root,ext = os.path.splitext(path)
	if ext in ['.html', '.inc', '.sh', '.php', '.js', '.css']:
		return True
	else:
		return False

# add matching include to results
def addMatch(M, P):
	name = P[48:]
	#name = P
	if name in all:
		curlist = all[name]
		if M in curlist:
			pass
		else: 
			curlist.append(M)
			all[name] = curlist
	else:
		all[name] = [M]

			
# main logic - iterate over files, grep for includes and add them to file's list
for root, dirs, files in os.walk(inputFolder):
	for file in files:
		path = os.path.join(root, file)
		if include(path):
			try:
				with open(path, 'rU') as f:
					name = path[48:]
					listoffiles.append(name)
					try:
						for line in f:
							match = inc.search(line)
							if match != None:
								hit = match.group(1)
								addMatch(hit, path)
							match2 = nav.search(line)
							if match2 != None:
								hit2 = match2.group(1)
								addMatch(hit2, path)
							match3 = js.search(line)
							if match3 != None:
								hit3 = match3.group(1)
								addMatch(hit3, path)
					except UnicodeDecodeError as e:
						print ("UnicodeDecodeError {0}, {1}".format(e.object[e.start:e.end], path))
			except OSError as e:
				print ("OSError {0}, {1}, {2}".format(e.errno, e.strerror, path))
		else:
			continue

#build out list of files w/o include
with open("otherfiles.txt", 'w') as results:
	for file in listoffiles:
		if file not in all:
			results.writelines("{0}\n".format(file))
results.close()
		
# output results of include search
#with open(outputFile, 'w') as resultFile:
#	for key,value in all.items():
#		resultFile.writelines("{0}:::{1}\n".format(key,value))
#resultFile.close()