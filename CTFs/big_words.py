#!/usr/bin/env python

__description__ = "Dump biggest words from file, compare to known file and return possible results"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import os, sys


# check input and return path to encoded file
nargs = len(sys.argv)
print(nargs)
if not nargs == 2:
	print ("usage: %s encoded_file" % os.path.basename(sys.argv[0]))
	sys.exit()
else:
	filepath = sys.argv[1]
	
# parse encoded file list and return list of encoded words in order of length
def words_of_file(thefilepath, line_to_words=str.split):
	# initialize list that will contain biggest words
	ordered_e_words = []
	
	# open encoded file
	print("Opening encoded file")
	with open(thefilepath, 'rU') as the_file:
		print("Processing encoded words from file")
		for line in the_file:
			for word in line_to_words(line):
				if word not in ordered_e_words:
						ordered_e_words.append(word)
						print(word)
	the_file.close()
	return ordered_e_words.sort(key = len)

def get_big_words(
# opening known word file 
print("Opening word list file")
with open('~/Documents/Python_Scripts/word_list.txt', 'rU') as word_file:
	# process each line from word file
	print("Processing words from file")
	next_word = word_file.readline()
	while next_word:
		if len(next_word) >= 7:
			short_words.append(next_word)
			print(next_word)
		next_word = word_file.readline()		
word_file.close()
	
results = words_of_file(filepath)
	

# write results to file
print("Writing results to output file")
with open('~/Documents/Python_Scripts/large_encoded_words.txt', 'w') as resultFile:
	resultFile.writelines(results)
	print("Success! Check your file. Exiting.")
resultFile.close()