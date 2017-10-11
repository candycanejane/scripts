#!/usr/bin/env python

__description__ = "Fix base64 encoded emails"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import email, sys, os, string, base64
from email.generator import Generator

# check usage
nargs = len(sys.argv)
if nargs != 3:
	print "Usage: %s in_folder out_folder" % os.path.basename(sys.argv[0])
	sys.exit()
else:
	inputFolder = sys.argv[1]
	resultsFolder = sys.argv[2]

# decode base64 encoded email bodies
def b64fix(emlMsg):
	msg = email.message_from_file(emlMsg)
	msg_payload = msg.get_payload()
	decoded = base64.b64decode(msg_payload)
	msg.set_payload(decoded)
	
	return msg
	
for filename in os.listdir(inputFolder):
	path = os.path.join(inputFolder, filename)
	outPath = os.path.join(resultsFolder, filename)
	if not os.path.isfile(path):
		continue
	else:
		with open(path, 'rU') as eml:
			fixed_msg = b64fix(eml) 
			with open(outPath, 'w') as fixed_eml:
				g = Generator(fixed_eml)
				g.flatten(fixed_msg)
				fixed_eml.flush()
				fixed_eml.close()
			eml.close()