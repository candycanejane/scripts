#!/usr/bin/python

__description__ = "Convert OSX magic file to Linux-compatible signatures."
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import logging
from time import gmtime, strftime

# OSX Syntax
start = '\x5B'
content = '\x3E'

# Linux Syntax
spacer = '\x09\x09'
space = '\x09'
end = '\x0A'
classifier = 'string'
mime_format = '!:mime\x09'



"""
sample osx signature
[50:video/annodex]
>0= OggS
1>28= fishead 
2>56= CMML    +457
[50:text/x-subviewer]
>0= [INFORMATION]
"""

out_folder = '~/Documents/LAB/mime-type/out2'

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='~/Documents/LAB/mime-type/out2/sigs.log', filemode='w', level=logging.INFO)

fname = 0

def convertnum(num):
    s = ''
    for i in xrange(int(num)):
        s = s + '>'
    return s

try:
    with open('osx_opt_local_share_mime_magic.txt', 'rb') as file:
        text = file.read()
        sigs = text.split('\n[')
        for sig in sigs:
            strings = []
            partial1 = sig.split(']', 1)
            partial2 = partial1[0].split(':')
            mime = partial2[1]
            mime_name = mime.split('/')[1]
            logging.info(mime)
            
            temp = partial1[1][1:]
            temp1 = temp.lstrip('>')
            temp2 = temp1.replace('1>', '>>')
            temp3 = temp2.replace('2>', '>>>')
            temp4 = temp3.replace('3>', '>>>>')
            list_of_sigs = temp4.split('\n>')
            for s in list_of_sigs:
                partial5 = s.split('=')
                offset = partial5[0]
                byte_code = partial5[1][2:].rstrip('\n')
                out = "{0}{1}{2}{3}{4}{5}{6}{7}".format(str(offset), space, classifier, spacer, byte_code, spacer, mime, end)
                strings.append(out)
                if out[0].isdigit():
                    mime_line = mime_format + mime + end
                    strings.append(mime_line)
            
            header = "\n#------------------------------------------------------------------------------\n# $File: {0},v 1.0 {1} jforness Exp $\n# {2}:  file(1) magic for {3}\n#\n".format(mime_name, strftime("%Y-%m-%d %H:%M:%S", gmtime()), mime_name, mime)
            # write out the signatures
            with open('{0}/{1}_{2}.txt'.format(out_folder, str(fname), mime_name), 'wb') as sig_file:
                strings.insert(0, header)
                sig_file.writelines(strings)
                fname += 1
            sig_file.close() 
    file.close()
except Exception as e:
    print e
        