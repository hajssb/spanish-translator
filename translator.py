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

def is_verb(tag):
	return "VB" in tag

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

def is_reverse_punctuation(word):
	return word.decode('utf-8') == u'\u00bf' or word.decode('utf-8') == u'\u00A1'

def is_vowel(char):
	return char == 'a' or char == 'e' or char == 'i' or char == 'o' or char == 'u'

def delete_repeated_words(english_words):
	ret = []
	for word in english_words:
		if len(ret) == 0 or word != ret[-1]:
			ret.append(word)
	return ret

def replace_a_with_an(sentence):
	return re.sub("(^| )a ([aeiou]\w+)", lambda m: m.group(1) + "an " + m.group(2), sentence)

def remove_a_before_percent(sentence):
	return re.sub("(^| )a ([0-9]+ %)", lambda m: m.group(1) + m.group(2), sentence)

def remove_the_before_has(sentence):
	return re.sub("(^| )the has ", lambda m: m.group(1) + "has ", sentence)

def replace_not_i(sentence):
	return re.sub("(^| )not i ", lambda m:m.group(1) + "i don &apos;t ", sentence)

def replace_regex(english_words):
	sentence = " ".join(english_words)

	sentence = replace_a_with_an(sentence)
	sentence = remove_a_before_percent(sentence)
	sentence = remove_the_before_has(sentence)
	sentence = replace_not_i(sentence)

	return sentence.split()

def improvements(english_words):
	english_words = rearrange_pos(english_words)
	english_words = replace_regex(english_words)
	english_words = delete_repeated_words(english_words)
	return english_words

def infinitive_verbs(span_sent):
	return re.sub("(^| )([a-zA-Z]+ar)", lambda m: m.group(1) + "a " + m.group(2), span_sent)

def regex_improvements(spanish_sentence):
	as_str = " ".join(spanish_sentence)
	# as_str = infinitive_verbs(as_str)
	return as_str.split()

def improvements_spanish(spanish_sentence):
	spanish_sentence = regex_improvements(spanish_sentence)
	return spanish_sentence

def translate_sentence(spanish_sentence):
	english_words = []

	spanish_sentence = improvements_spanish(spanish_sentence)

	for spanish_word in spanish_sentence:
		if is_reverse_punctuation(spanish_word):
			continue

		translated_word = spanish_word
		if spanish_word in bitext.keys():
			translated_word = bitext[spanish_word]

		translated_word = convert_escaped_chars(translated_word)
		english_words.append(translated_word)

	english_words = improvements(english_words)
	return english_words

if __name__ == '__main__':
	reload(sys)    # to re-enable sys.setdefaultencoding()
	sys.setdefaultencoding('utf-8')
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