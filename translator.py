import sys
import codecs
import re
from edit_distance import generate_all_one_edit

def ingest_model(model_filename):
	f = codecs.open(model_filename, 'r', "UTF-8")
	bitext = {}
	for line in f:
		split_up = line.split("::")
		bitext[split_up[0].rstrip()] = split_up[1].rstrip()
	return bitext

if __name__ == '__main__':
	bitext = ingest_model(sys.argv[2])

	file_to_translate = sys.argv[1]

	f = codecs.open('translation.out', 'w', "UTF-8")

	lines = codecs.open(file_to_translate, 'r', "UTF-8").readlines()
	for line_idx in range(0,len(lines)-1):
		line = lines[line_idx]
		spanish_words = list(map(lambda word: word.lower(), re.sub("[^\w]|[0-9]", " ", line, flags=re.UNICODE).split()))

		for spanish_word in spanish_words:
			translated_word = spanish_word
			if spanish_word in bitext.keys():
				translated_word = bitext[spanish_word]
			# else:
			# 	possible_errors = generate_all_one_edit(spanish_word)
			# 	for possible_error in possible_errors:
			# 		if possible_error in bitext.keys():
			# 			translated_word = bitext[possible_error]
			# 			break
			f.write(translated_word + " ")
		f.write("\n")

	line = lines[len(lines)-1]
	spanish_words = list(map(lambda word: word.lower(), re.sub("[^\w]|[0-9]", " ", line, flags=re.UNICODE).split()))
	for spanish_word in spanish_words:
		translated_word = spanish_word
		if spanish_word in bitext.keys():
			translated_word = bitext[spanish_word]
		# else:
		# 	possible_errors = generate_all_one_edit(spanish_word)
		# 	for possible_error in possible_errors:
		# 		if possible_error in bitext.keys():
		# 			translated_word = bitext[possible_error]
		# 			break
		f.write(translated_word + " ")