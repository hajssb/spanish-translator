from itertools import permutations
from collections import defaultdict
from stemming.porter2 import stem
import codecs
import re
from math import log

class ExpectationMaximization:
	def __init__(self, spanishFilename, englishFilename):
		self.translationProbabilities = dict()
		self.translationMap = {}
		self.languageModelFrequencies = defaultdict(int)
		self.learnProbabilities(spanishFilename, englishFilename)

	def getTranslationMap(self):
		return self.translationMap

	def learnProbabilities(self, spanishFilename, englishFilename):

		print("Getting sentences")
		# This is an array of dictionaries, i.e. [{spanish: ["yo", "soy", ...], english: ["i", "am", ...]}, {spanish:..., english:...}, ...]
		sentence_pairs = self.getSentencePairs(spanishFilename, englishFilename)

		print("Initializing probability table")
		# Initialize to have uniform probability for each word to translate to another
		all_spanish_words, all_english_words = self.initializeTranslationProbabilityTable(sentence_pairs)

		print("Doing EM")
		self.learnUntilConvergence(sentence_pairs, all_spanish_words, all_english_words)

	def getSentencePairs(self, spanishFilename, englishFilename):
		sentence_pairs = []
		spanishSentences = codecs.open(spanishFilename, 'r', 'UTF-8').readlines()
		englishSentences = codecs.open(englishFilename, 'r', 'UTF-8').readlines()

		# assume they are same length
		for i in range(0, len(spanishSentences)/4):
			new_sentence_pair = {}
			new_sentence_pair['spanish'] = \
			list(map(lambda word: word.lower(), re.sub("[^\w]|[0-9]", " ", spanishSentences[i], flags=re.UNICODE).split()))

			new_sentence_pair['english'] = \
			list(map(lambda word: word.lower(), re.sub("[^\w]|[0-9]", " ", englishSentences[i], flags=re.UNICODE).split()))
			sentence_pairs.append(new_sentence_pair)

		return sentence_pairs

	def initializeTranslationProbabilityTable(self, sentences):
		all_spanish_words = set()
		all_english_words = set()
		for i, sentence in enumerate(sentences):
			for spanish_word in sentence["spanish"]:
				all_spanish_words.add(spanish_word)
			for eng_word in sentence["english"]:
				all_english_words.add(eng_word)
				self.languageModelFrequencies[eng_word] += 1.1

		uniform_prob = 1 / float(len(all_english_words))

		for spanish_word in all_spanish_words:
			self.translationProbabilities[spanish_word] = defaultdict(lambda: uniform_prob)

		return all_spanish_words, all_english_words

	def learnUntilConvergence(self, sentence_pairs, all_spanish_words, all_english_words):
		oldBestTranslationForEachWord = defaultdict(int)
		for i in range(0,2):
			print("Iterating")
			counts_of_coocurrences = {}
			for span_word in all_spanish_words:
				counts_of_coocurrences[span_word] = defaultdict(int)
			totals_spanish = defaultdict(int)

			best_translation_map = {}

			print("Doing all sentences")
			for idx, sentence_pair in enumerate(sentence_pairs):
				total_english_words_sent = defaultdict(int)
				for eng_word in sentence_pair['english']:
					for spanish_word in sentence_pair['spanish']:
						total_english_words_sent[eng_word] += self.translationProbabilities[spanish_word][eng_word]
				for eng_word in sentence_pair['english']:
					for spanish_word in sentence_pair['spanish']:
						counts_of_coocurrences[spanish_word][eng_word] += self.translationProbabilities[spanish_word][eng_word] / total_english_words_sent[eng_word]
						totals_spanish[spanish_word] += self.translationProbabilities[spanish_word][eng_word] / total_english_words_sent[eng_word]

			print("Updating probabilities for each word pair")
			for span_word in all_spanish_words:
				best_translation = ""
				best_prob = float('-inf')

				probabilities_for_spanish_word = self.translationProbabilities[span_word]
				counts_of_span_word_coocurrences = counts_of_coocurrences[span_word]
				total = totals_spanish[spanish_word]
				for engl_word in all_english_words:
					probabilities_for_spanish_word[engl_word] = counts_of_span_word_coocurrences[engl_word] / total
					# probabilities_for_spanish_word[engl_word] *= log(self.languageModelFrequencies[engl_word], 10)
					if probabilities_for_spanish_word[engl_word] > best_prob:
						best_translation = engl_word
						best_prob = probabilities_for_spanish_word[engl_word]

				best_translation_map[span_word] = best_translation

			print("Checking for convergence")
			self.translationMap = best_translation_map
			if self.bestTranslationHasConverged(best_translation_map, oldBestTranslationForEachWord):
				self.translationMap = best_translation_map
				return
			else:
				oldBestTranslationForEachWord = best_translation_map

	def computeBestTranslationForEachWord(self, heaps):
		print("Computing best translation for each word")
		bestTranslationForWord = dict()
		for spanish_word in self.translationProbabilities.keys():
			bestTranslationForWord[spanish_word] = heappop(heaps[spanish_word])[1]
		return bestTranslationForWord

	def bestTranslationHasConverged(self, newBestTranslationForEachWord, oldBestTranslationForEachWord):
		print("Comparing old best translation to new")
		for spanish_word in newBestTranslationForEachWord:
			if newBestTranslationForEachWord[spanish_word] != oldBestTranslationForEachWord[spanish_word]:
				return False
		return True

if __name__ == '__main__':
	x = ExpectationMaximization('es-en/train/europarl-v7.es-en.es', 'es-en/train/europarl-v7.es-en.en')
	print("Writing to file")
	f = codecs.open("without_lang_model.out", "w", "UTF-8")
	for spanish_word, eng_word in x.getTranslationMap().items():
		f.write(spanish_word + "::" + eng_word + "\n")
	f.close()

