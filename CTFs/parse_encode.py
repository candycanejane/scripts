#!/usr/bin/python

__description__ = "script to decode substitution-based cypher using word file"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import os, sys, struct

# check for correct number of arguments
nargs = len(sys.argv)
if not nargs == 3:
	print ("usage: %s encoded_file word_file" % os.path.basename(sys.argv[0]))
	sys.exit()
else:
	e_filepath = sys.argv[1]
	w_filepath = sys.argv[2]

# given encoded file, extract sorted list of unique words
def big_words_of_file(thefilepath):
	#open encoded file
	print("Opening encoded file")
	with open(thefilepath, 'rU') as the_file:
		print("Processing encoded words from file")
		list_of_words = the_file.read().replace('\n',' ').split()
		e_words = [word for word in list_of_words if len(word) == 7]
	the_file.close()
	return e_words

# given a word file return a list of words
def get_word_list(thefilepath):
	#opening known word file 
	print("Opening word list file")
	with open(thefilepath, 'rU') as word_file:
		#process each line from word file
		print("Processing words from file")
		list_of_all_words = word_file.read().lower().split('\n')
		big_words = [word for word in list_of_all_words if len(word) == 7]
	word_file.close()
	return big_words

# given a list of known words and a list of encoded words greater than 8 characters, returns dictionary of encoded words w/ possible matching words
def match_possible_words(list_of_known_words, list_of_encoded_words):
	matches = {}
	for eword in list_of_encoded_words:
		list_words = [kword for kword in list_of_known_words if len(kword) == len(eword)]
		list_position_match = [kword for kword in list_words if has_same_dup_letters(eword,kword)]
		matches[eword] = list_position_match
	return matches
	

# checks whether two words have duplicate letters and if they are in the same position in each string
def has_same_dup_letters(eword, kword):
	l_eword = list(eword)
	l_kword = list(kword)
	
	dict_eword = {}
	dict_kword = {}
	# check if the encoded word has duplicate letters, if so return their index values
	if len(l_eword)!=len(set(l_eword)) and len(l_kword)!=len(set(l_kword)):
		for l in l_eword:
			letter_index = [p for p,c in enumerate(l_eword) if c == l]
			if l not in dict_eword:
				dict_eword[l] = letter_index
		for l in l_kword:
			letter_index2 = [p for p,c in enumerate(l_kword) if c == l]
			if l not in dict_kword:
				dict_kword[l] = letter_index2

		return sorted(dict_eword.values()) == sorted(dict_kword.values())
	else:
		return False
			
	
	
b_encoded_words = big_words_of_file(e_filepath)
b_known_words = get_word_list(w_filepath)
results = match_possible_words(b_known_words, b_encoded_words)
for (k,v) in results.items():
	print k,v,'\n'
	

# write results to file
print("Writing results to output file")
with open('~/Documents/Python_Scripts/possible_words.txt', 'w') as resultFile:
	resultFile.writelines(results)
	print("Success! Check your file. Exiting.")
resultFile.close()