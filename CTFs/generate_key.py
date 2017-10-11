#!/usr/bin/python

__description__ = "script to decode encoded file based on key"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

import os, sys, string

# check for correct number of arguments
nargs = len(sys.argv)
print(nargs)
if not nargs == 3:
	print ("usage: %s encoded_file word_file" % os.path.basename(sys.argv[0]))
	sys.exit()
else:
	e_filepath = sys.argv[1]
	w_filepath = sys.argv[2]

# open a file and parse text into list of words
def open_and_parse(thefilepath):
	# open encoded file
	print("Opening file")
	with open(thefilepath, 'rU') as the_file:
		print("Processing words from file")
		list_of_words = the_file.read().lower().replace('\n',' ').split()
	return list_of_words
	the_file.close()
	
# given a list of words, extract unique words with 8 or more characters
def get_big_words(listofwords):
	big_words = [word for word in listofwords if len(word) >= 8]
	return set(big_words)

# given a list of words, return words with only one character
def one_letter_words(listofwords):
	small_words = [word for word in listofwords if len(word) == 1]
	return set(small_words)

# generate letter frequency from a list of words
def list_letter_frequency(listofwords):
	# initialize dictionary that will calculate frequency of letters
	alphabet = dict.fromkeys(string.ascii_lowercase, 0)

	all_words = ' '.join(listofwords)
	all_letters = filter(str.isalnum,all_words)
	list_of_letters = list(all_letters)
	
	# add +1 to dictionary for each letter matched
	for i in list_of_letters:
		alphabet[i] += 1		
	return alphabet	
	
# given a list of known words and a list of encoded words greater than 8 characters, returns dictionary of encoded words w/ possible matching words
def match_possible_words(list_of_encoded_words, list_of_known_words):
	matches = {}
	for eword in list_of_encoded_words:
		list_words = [kword for kword in list_of_known_words if len(kword) == len(eword)]
		list_position_match = [kword for kword in list_words if has_same_dup_letters(eword,kword)]
		matches[eword] = list_position_match
	return matches

# given a word, create a dictionary of letters to their corresponding indexes
def create_letter_index(word):
	# initialize dictionary that will contain the results
	dict_word = {}
	l_word = list(word)
	for l in l_word:
		letter_index = [p for p,c in enumerate(l_word) if c == l]
		if l not in dict_word:
			dict_word[l] = letter_index
	return dict_word

# checks whether two words have duplicate letters and if they are in the same position in each string
def has_same_dup_letters(eword, kword):
	l_eword = list(eword)
	l_kword = list(kword)

	# check if the encoded word has duplicate letters, if so return their index values
	if len(l_eword)!=len(set(l_eword)) and len(l_kword)!=len(set(l_kword)):
		eword_index = create_letter_index(eword)
		kword_index = create_letter_index(kword)

		return sorted(eword_index.values()) == sorted(kword_index.values())
	else:
		return False

def min_item_from_dict(dict):
	# retrieve the dictionary item with the smallest number of values
	min = 50;
	for (k,v) in dict.items():
		if min > len(v):
			min = v
			closest = {k:v}
	return closest

# assign "a" or "i' first, given possible matches
def assign_other_letters(key, word):

def still_possible_match(key, eword, kword):
	if not key_full(key)
		for l in eword:
			
	else:
		return False

def key_full(key):
	return 0 not in key.values()

def assign_letters(key, list_of_encoded_words, list_of_known_words):
	# determine one-letter encoded words
	e_one_letter = one_letter_words(list_of_encoded_words)
		
	# pull out only the big words first
	e_big_words = get_big_words(list_of_encoded_words)
	k_big_words = get_big_words(list_of_known_words)
	
	while not key_full
	# generate dictionary of potential matches: encoded word to list of known words that
	# are possible matches
	matches = match_possible_words(e_big_words, k_big_words)
	closest_match = min_item_from_dict(matches)
	c_key = closest_match.keys()
	c_value = closest_match.values()

	# assign "a" and "i" based on one-letter words
	e_word = create_letter_index(c_key)
	
	if e_one_letter[0] in e_word:
		l = e_one_letter[0]
		idx = e_word.find(l)
		for word in closest_match.values():
			char = word[idx]
			if char == l and key[char] == 0:
				key[char] = l
				assign_other_letters(key, e_word, word)
	else if e_one_letter[1] in e_word:
		l = e_one_letter[1]
		idx = e_word.find(l)
		for word in closest_match.values():
			char = word[idx]
			if char == l and key[char] == 0:
				key[char] = l
				assign_other_letters(key, e_word, word)
	else:
		matches.pop(c_key)
	

# generate starter key		
key = dict.fromkeys(string.ascii_lowercase, 0)

# extract words from encoded word file and known word file
encoded_words = open_and_parse(e_filepath)
known_words = open_and_parse(w_filepath)

decode_key = assign_letters(key, encoded_words, known_words)

# testing results by printing to screen
print one_letter_words(list_of_words)
print word_freq