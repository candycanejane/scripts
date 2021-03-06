#!/usr/bin/python

__description__ = "Convert OSX magic file to Linux-compatible signatures."
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import logging

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
[90:application/vnd.stardivision.writer]
>2089= 
StarWriter
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
    with open('testosxparse.txt', 'rb') as file:
        text = file.read()
        sigs = text.split('\n[')
        for sig in sigs:
            strings = []
            partial1 = sig.split(']', 1)
            partial2 = partial1[0].split(':')
            mime = partial2[1]
            mime_name = mime.split('/')[1]
            logging.info(mime)
            
            list_of_sigs = partial1[1][1:].split('\n')
            for s in list_of_sigs:
                num = s[0]
                if num.isdigit():
                    extra = convertnum(num)
                    mod_sig = extra + s[2:]
                    partial4 = mod_sig.split('=')
                    offset = partial4[0]
                    byte_code = partial4[1][2:].rstrip('\n')
                else:
                    partial5 = s[1:].split('=')
                    offset = partial5[0]
                    byte_code = partial5[1][2:].rstrip('\n')
                out = str(offset) + space + classifier + spacer + byte_code + spacer + mime + end
                strings.append(out)
            
            # write out the signatures
            with open('{0}/{1}_{2}.txt'.format(out_folder, str(fname), mime_name), 'wb') as sig_file:
                final_line = mime_format + mime + end
                strings.append(final_line)
                sig_file.writelines(strings)
                fname += 1
            sig_file.close() 
    file.close()
except Exception as e:
    print e
        