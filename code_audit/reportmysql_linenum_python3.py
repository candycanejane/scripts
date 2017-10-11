#!/usr/bin/python

__description__ = "Search code repo and return most problematic SQL injection hits"
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

#mysql and quotesmart() regex
sql = re.compile(r'([\"\'](?=select |delete |insert |execute |mysql_query|update )[\w\d,._\- \$%=\(\)\[\]\'\"{}]*(?=\';|\";|\);|\];))', flags=re.I)
quote = re.compile(r'quote_smart')
var = re.compile(r'\$_[A-Z]*\[')


# only include certain files in search
def include(path):
	root,ext = os.path.splitext(path)
	if ext in ['.html', '.inc', '.sh', '.php', '.js', '.css']:
		return True
	else:
		return False
		
# add matches, line number, and path of results
def addLineMatch(M, L, P):
	name = P[48:]
	line = "{0}: {1}".format(L,M)
	if name in all:
		curlist = all[name]
		curlist.append(line)
		all[name] = curlist
	else:
		all[name] = [line]

			
# main logic - iterate over files, grep for possible sql injection and add them to file's list
for root, dirs, files in os.walk(inputFolder):
	for file in files:
		path = os.path.join(root, file)
		if include(path):
			try:
				with open(path, 'rU') as f:
					try:
						for num, line in enumerate(f,1):
							match = sql.search(line)
							if match != None:
								match2 = var.search(line)
								if match2 != None:
									match3 = quote.search(line)
									if match3 == None:
										clean_line = line.strip()
										addLineMatch(clean_line, num, path)
					except UnicodeDecodeError as e:
						print ("UnicodeDecodeError {0}, {1}".format(e.object[e.start:e.end], path))
			except OSError as e:
				print ("OSError {0}, {1}, {2}".format(e.errno, e.strerror, path))
		else:
			continue
		
# output results of include search
with open("mysql_hits2wnums.txt", 'w') as resultFile:
	for key,value in all.items():
		for l in value:
			resultFile.writelines("{0}\t{1}\n".format(key,l))
resultFile.close()