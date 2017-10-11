#!/usr/bin/python

__description__ = "Find exact duplicate files using MD5 hash"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import sys, os, string
from io import BufferedIOBase
import hashlib


# check usage
nargs = len(sys.argv)
if nargs != 3:
	print("Usage: %s in_folder out_file".format(os.path.basename(sys.argv[0])))
	sys.exit()
else:
	inputFolder = sys.argv[1]
	outputFile = sys.argv[2]

# hashes stored as {hash:[filename list]}
all = {}

def addHash(H, P):
	name = P[48:]
	if H in all:
		curlist = all[H] 
		curlist.append(name)
		all[H] = curlist
	else:
		all[H] = [name]

# only include html, inc, sh, php, js, and css files in search
def include(path):
	root,ext = os.path.splitext(path)
	if ext in ['.html', '.inc', '.sh', '.php', '.js', '.css']:
		list = path.split('/')
		if 'jpgraph' in list:
			return False
		else: return True
	else:
		return False

# main logic - iterate over files, hash and return list of duplicates
for root, dirs, files in os.walk(inputFolder):
	for file in files:
		path = os.path.join(root, file)
		if include(path):
			try:
				with open(path, 'rb') as f:
					data = f.read()
					h = hashlib.md5()
					h.update(data)
					hash = h.hexdigest()
					addHash(hash, path)
			except OSError as e:
				print ("OSError {0}, {1}, {2}".format(e.errno, e.strerror, path))
		else:
			continue

# output results of duplicate files only
with open(outputFile, 'w') as resultFile:
	for key,value in all.items():
		if len(value) > 1:
			resultFile.writelines("{0}:{1}\n".format(key,value))
resultFile.close()