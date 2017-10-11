#!/usr/bin/env python

__description__ = "sanitizeEMLs.py will remove attachments from .eml messages; it will leave the original reference to the attachment (ie. it will still look like an attachment in Outlook, but there will be no payload)
"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import email, sys, os, string, hashlib
from email.generator import Generator 
from shutil import copy

# check usage
nargs = len(sys.argv)
if nargs != 3:
	print "Usage: %s in_folder out_folder" % os.path.basename(sys.argv[0])
	sys.exit()
else:
	inputFolder = sys.argv[1]
	resultsFolder = sys.argv[2]

# check to see if message contains an attachment, if so, returns True
def containsAttach(emlMsg):
	flag = False
	msg = email.message_from_file(emlMsg)
	
	for part in msg.walk():
		disp = part.get("Content-Disposition",None)
		#debug: print disp 
		if disp == None:
			continue
			#debug: print part.get_payload()
		elif disp.split(';')[0] == "attachment":
			flag = True 
			#debug: print part.get_payload()
	emlMsg.seek(0)
	return flag

# set attachment payload to None 
def sanitize(emlMsg):
	msg = email.message_from_file(emlMsg)
	
	for part in msg.walk():
		content = part.get_content_type()
		disp = part.get("Content-Disposition",None)
		#debug: print disp 
		if ((disp == None) | (content == "message/rfc822") | (content == "message/delivery-status")):
			continue
			#debug: print part.get_payload()
		elif disp.split(';')[0] == "attachment":
			part.set_payload(None)
			#debug: print part.get_payload()
	
	return msg

# main logic - interate over files in folder, open & check if contains attachment, if yes, sanitize and copy to output folder; if no, copy to output folder
for filename in os.listdir(inputFolder):
	path = os.path.join(inputFolder, filename)
	if not os.path.isfile(path):
		continue
	else:
		with open(path, 'rU') as eml:
			# hash contents and use for filename
			MD5_filename = hashlib.md5(eml.read()).hexdigest()
			eml.seek(0)
			#debug: print MD5_filename 
			folders = inputFolder.split('\\')
			src_folder = folders[-1]
			outPath = os.path.join(resultsFolder, 's_'+src_folder+'_'+MD5_filename+'.eml')
			#debug: print outPath
			# if contains attachment, sanitizes and builds new .eml w/ result 
			if containsAttach(eml):
				print "Found an attachment in %s. Deleting payload..." % filename
				clean_msg = sanitize(eml) 
				with open(outPath, 'w') as clean_eml:
					g = Generator(clean_eml)
					g.flatten(clean_msg)
					clean_eml.flush()
					clean_eml.close()
			else:
				copy(path, resultsFolder+'\\'+src_folder+'_'+MD5_filename+'.eml')
		eml.close()