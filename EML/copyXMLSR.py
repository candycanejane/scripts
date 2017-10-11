#!/usr/bin/env python

__description__ = "copies the files containing positive search results; works with dtSearch exported XML file"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import os, sys, string, hashlib
import xml.etree.ElementTree as ET
from shutil import copy
 

# check usage
nargs = len(sys.argv)
if nargs != 3:
	print "Usage: %s XML_file SR_folder" % os.path.basename(sys.argv[0])
	sys.exit()
else:
	inputXML = sys.argv[1]
	resultsFolder = sys.argv[2]

# parse XML and copy files to given folder
with open(inputXML, 'rU') as XML_file:
	tree = ET.parse(XML_file)
	root = tree.getroot()
	for filename in root.iter('Filename'):
		# open EML, hash contents and provide hash as new filename
		with open(filename.text, 'rU') as EML:
			MD5_filename = hashlib.md5(EML.read()).hexdigest()
			EML.close()
		# rename copied files to <folder>_<hash>.eml/txt
		fullpath = filename.text.split('\\')
		src_folder = fullpath[-2]
		src_ext = fullpath[-1][-4:]
		if filename.text.endswith(('.eml','.txt')):
			copy(filename.text, resultsFolder+'\\'+src_folder+'_'+MD5_filename+src_ext)
		else:
			copy(filename.text, resultsFolder+'\\'+src_folder+'_'+MD5_filename)
	XML_file.close()