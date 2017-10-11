#!/usr/bin/python

__description__ = "match unique words from substitution file to word possibilities from word file"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import os, sys, string

#check for correct number of arguments
nargs = len(sys.argv)
if not nargs == 3:
	print ("usage: %s encoded_file word_file" % os.path.basename(sys.argv[0]))
	sys.exit()
else:
	e_filepath = sys.argv[1]
	w_filepath = sys.argv[2]
	
#initialize list that will contain single and double-letter words
unique_words = []

#open word file on mac/linux
print("Opening encoded file")
with open(e_filepath, 'rU') as e_file:
	#process each line from word file
	print("Processing words from file")
	next_word = word_file.readline()
	while next_word:
		if len(next_word) <= 3:
			short_words.append(next_word)
			print(next_word)
		next_word = word_file.readline()		
word_file.close()

