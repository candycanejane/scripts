#!/usr/bin/python

__description__ = "Search code repo and return XSS hits"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import sys, os, string, re
from io import BufferedIOBase

# check usage
nargs = len(sys.argv)
if nargs != 2:
	print("Usage: %s in_folder".format(os.path.basename(sys.argv[0])))
	sys.exit()
else:
	inputFolder = sys.argv[1]

# includes stored as {file:[hits list]}
all = {}

# xss regex, exclude hits found in comments
xss = re.compile(r'[^//]echo.*\$.*;', flags=re.I)
xss_clean = re.compile(r'xss_clean', flags=re.I)

# only include relevant files in search
def include(path):
	root,ext = os.path.splitext(path)
	if ext in ['.html', '.inc', '.sh', '.php', '.js', '.css']:
		return True
	else:
		return False

#add matches, line number and path of results
def addLineMatch(M, L, P):
	name = P[48:]
	line = "[+] {0} {1}".format(L,M)
	if name in all:
		curlist = all[name]
		curlist.append(line)
		all[name] = curlist
	else:
		all[name] = [line]
			
# main logic - iterate over files, grep for possible xss and add them to file's list
for root, dirs, files in os.walk(inputFolder):
	for file in files:
		path = os.path.join(root, file)
		if include(path):
			try:
				with open(path, 'rU') as f:
					try:
						for num, line in enumerate(f,1):
							match = xss.search(line)
							if match != None:
								match2 = xss_clean.search(line)
								if match2 == None:
									clean_line = line.strip()
									addLineMatch(clean_line, num, path)
					except UnicodeDecodeError as e:
						print ("UnicodeDecodeError {0}, {1}".format(e.object[e.start:e.end], path))
			except OSError as e:
				print ("OSError {0}, {1}, {2}".format(e.errno, e.strerror, path))
		else:
			continue
		
# output results of include search
with open("xss_hits2.txt", 'w') as resultFile:
	for key,value in all.items():
		resultFile.writelines("{0}\t{1}\n".format(key,value))
resultFile.close()