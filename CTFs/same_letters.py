#!/usr/bin/python

__description__ = "script to decode substitution-based cypher using word file"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import os, sys

# check for correct number of arguments
nargs = len(sys.argv)
if not nargs == 3:
	print ("usage: %s encoded_file word_file" % os.path.basename(sys.argv[0]))
	sys.exit()
else:
	e_word = sys.argv[1]
	w_word = sys.argv[2]

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

print has_same_dup_letters(e_word,w_word)