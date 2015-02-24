import sys
import codecs
import re
from edit_distance import generate_all_one_edit
from nltk import pos_tag

def ingest_model(model_filename):
	f = codecs.open(model_filename, 'r', "UTF-8")
	bitext = {}
	for line in f:
		split_up = line.split("::")
		bitext[split_up[0].rstrip()] = split_up[1].rstrip()
	return bitext

def should_swap(tag, nextTag, firstWord, nextWord):
	return ((tag == "NN" or tag == "NNS" or tag == "NNP") and (nextTag == "JJ" or nextTag == "MD")) or \
	(tag == "RB" and nextTag == "VBZ") or \
	(firstWord == "states" and nextWord == "united")

def rearrange_pos(english_words):
	tags = [x[1] for x in pos_tag(english_words)]
	i = 0
	while i < len(english_words)-1:
		if should_swap(tags[i], tags[i+1], english_words[i], english_words[i+1]):
			english_words[i], english_words[i+1] = english_words[i+1], english_words[i]
			i += 2
		else:
			i += 1
	return english_words

def convert_escaped_chars(word):
	if word == "quot":
		return "&quot;"
	if word == "apos":
		return "&apos;"
	return word

def should_remove(word):
	# Reverse ? and !
	# TODO: This is not working
	return word == u'\xc2\xbf' or word == u'\xc2\xa1'

def is_vowel(char):
	return char == 'a' or char == 'e' or char == 'i' or char == 'o' or char == 'u'

def replace_a_and(english_words):
	for i in range(0, len(english_words)-1):
		if english_words[i] == "a" and is_vowel(english_words[i+1][0]):
			english_words[i] = "an"

def translate_sentence(spanish_sentence):
	english_words = []
	for spanish_word in spanish_sentence:
		if should_remove(spanish_word):
			continue

		translated_word = spanish_word
		if spanish_word in bitext.keys():
			translated_word = bitext[spanish_word]

		translated_word = convert_escaped_chars(translated_word)
		english_words.append(translated_word)

	english_words = rearrange_pos(english_words)
	replace_a_and(english_words)
	return english_words

if __name__ == '__main__':
	bitext = ingest_model(sys.argv[2])

	file_to_translate = sys.argv[1]

	f = codecs.open('translation_pos.out', 'w', "UTF-8")

	lines = codecs.open(file_to_translate, 'r', "UTF-8").readlines()
	for line_idx in range(0,len(lines)-1):
		line = lines[line_idx]
		spanish_sentence = line.lower().split()

		english_sentence = translate_sentence(spanish_sentence)

		for eng_word in english_sentence:
			f.write(eng_word + " ")
		f.write("\n")

	line = lines[len(lines)-1]
	spanish_sentence = line.lower().split()
	english_sentence = translate_sentence(spanish_sentence)
	for eng_word in english_sentence:
		f.write(eng_word + " ")