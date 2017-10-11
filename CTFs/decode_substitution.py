#!/usr/bin/python

__description__ = "script to decode encoded file based on given key"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import os, sys, string
from itertools import izip
import itertools
from string import maketrans

# check for correct number of arguments
nargs = len(sys.argv)
print(nargs)
if not nargs == 2:
	print ("usage: %s encoded_file" % os.path.basename(sys.argv[0]))
	sys.exit()
else:
	filepath = sys.argv[1]

key = {
'a':'q',
'b':'c',
'c':'a',
'd':'r',
'e':'s',
'f':'v',
'g':'k',
'h':'g',
'i':'l',
'j':'z
',
'k':'p',
'l':'d',
'm':'b',
'n':'y',
'o':'h',
'p':'e',
'q':'u',
'r':'m',
's':'o',
't':'x',
'u':'j',
'v':'t',
'w':'n',
'x':'i',
'y':'w',
'z':'f'}

trans_key = maketrans("".join(key.values()), "".join(key.keys()))

# open encoded file
print("Opening encoded file")
with open(filepath, 'rU') as the_file:
	print("Processing encoded words from file")
	file = the_file.read()
	results = file.translate(trans_key)
	print results
the_file.close()


	
# write results to file
print("Writing results to output file")
with open('~/Documents/Python_Scripts/test_decode.txt', 'w') as resultFile:
	resultFile.writelines(results)
	print("Success! Check your file. Exiting.")
resultFile.close()
