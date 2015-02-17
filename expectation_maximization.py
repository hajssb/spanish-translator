from itertools import permutations

class ExpectationMaximization:
	def __init__(self, spanishFilename, englishFilename):
		self.translationProbabilities = dict()
		self.learnProbabilities(spanishFilename, englishFilename)

	def learnProbabilities(self, spanishFilename, englishFilename):

		print("Getting sentences")
		# This is an array of dictionaries, i.e. [{spanish: ["yo", "soy", ...], english: ["i", "am", ...]}, {spanish:..., english:...}, ...]
		sentences = self.getSentences(spanishFilename, englishFilename)

		print("Initializing probability table")
		# Initialize to have uniform probability for each word to translate to another
		self.initializeTranslationProbabilityTable(sentences)

		print("Generating alignments")
		# In the form: [[[0, 1, 2, 3], [0, 1, 2, 3]], [[alignment_1], [alignment_2]], ...]
		allPossibleAlignments = self.generateAllPossibleAlignments(sentences)

		print("Doing EM")
		learnUntilConvergence(sentences, allPossibleAlignments)

	def getSentences(self, spanishFilename, englishFilename):
		sentences = []
		spanishSentences = open(spanishFilename).readlines()
		englishSentences = open(englishFilename).readlines()

		# assume they are same length
		for i in range(0, len(spanishSentences)):
			new_sentence = {}
			new_sentence['spanish'] = spanishSentences[i].split(' ')
			new_sentence['english'] = englishSentences[i].split(' ')
			sentences.append(new_sentence)

		return sentences

	def initializeTranslationProbabilityTable(self, sentences):
		all_spanish_words = set()
		all_english_words = set()
		for i, sentence in enumerate(sentences):
			for spanish_word in sentence["spanish"]:
				all_spanish_words.add(spanish_word)
			for eng_word in sentence["english"]:
				all_english_words.add(eng_word)

		uniform_prob = 1 / len(all_english_words)

		for spanish_word in all_spanish_words:
			self.translationProbabilities[spanish_word] = dict()
			for eng_word in all_english_words:
				self.translationProbabilities[spanish_word][eng_word] = uniform_prob

	def generateAllPossibleAlignments(self, sentences):
		# TODO: Can't store permutations like this! Taking too much memory
		allPossibleAlignments = []
		for i, sentence in enumerate(sentences):
			print("Generating alignments for sentence " + str(i))
			total_num_spanish_words = len(sentence["spanish"])
			total_num_english_words = len(sentence["english"])
			print("perms " + str(total_num_spanish_words) + " " + str(total_num_english_words))
			allPossibleAlignments.append(self.generateAllPermutations(total_num_spanish_words, total_num_english_words))

		return allPossibleAlignments

	def generateAllPermutations(self, total_num_spanish_words, total_num_english_words):
		return [list(x) for x in permutations(range(total_num_spanish_words), total_num_english_words)]

	def learnUntilConvergence(self, sentences, allPossibleAlignments):
		oldBestTranslationForEachWord = self.computeBestTranslationForEachWord()
		while True:
			print("Iterating")
			probabilitesForEachAlignment = self.eStep(sentences, allPossibleAlignments)
			self.mStep(sentences, allPossibleAlignments, probabilitesForEachAlignment)
			newBestTranslationForEachWord = self.computeBestTranslationForEachWord()

			if self.bestTranslationHasConverged(newBestTranslationForEachWord, oldBestTranslationForEachWord):
				break
			else:
				oldBestTranslationForEachWord = newBestTranslationForEachWord

	def computeBestTranslationForEachWord(self):
		bestTranslationForWord = dict()
		for spanish_word in self.translationProbabilities.keys():
			bestTranslation = ""
			bestProbability = 0
			probabilitiesForSpanishWord = self.translationProbabilities[spanish_word]
			for eng_word, probability in probabilitiesForSpanishWord.items():
				if probability > bestProbability:
					bestProbability = probability
					bestTranslation = eng_word
			bestTranslationForWord[spanish_word] = bestTranslation
		return bestTranslationForWord

	def eStep(self, sentences, allPossibleAlignments):
		probabilitesForEachAlignment = []
		for i, sentence in enumerate(sentences):
			probabilitiesForSentence = []
			probabilitesForEachAlignment.append(probabilities)
			alignmentsForSentence = allPossibleAlignments[i]

			for alignment in alignmentsForSentence:
				probabilityForAlignment = 1
				sumOfProbabilitiesForSentence = 0

				for word_idx, spanish_word in enumerate(sentence['spanish']):
					probabilityForAlignment *= self.translationProbabilities[spanish_word][sentence['english'][alignment[word_idx]]]

				sumOfProbabilitiesForSentence += probabilityForAlignment
				probabilitiesForSentence.append(probabilityForAlignment)

				# Normalize
				for i in range(0, len(probabilitiesForSentence)):
					probabilitiesForSentence[i] /= sumOfProbabilitiesForSentence

			probabilitesForEachAlignment.append(probabilitiesForSentence)

		return probabilitesForEachAlignment
				

	def mStep(self, sentences, allPossibleAlignments, probabilitesForEachAlignment):
		# First zero out all probabilities
		for spanish_word in self.translationProbabilities:
			for eng_word in self.translationProbabilities[spanish_word]:
				self.translationProbabilities[spanish_word][eng_word] = 0

		# For each translated word pair, add the probability of the alignment to the table
		for sentence_idx, sentence in enumerate(sentences):
			for alignment_idx, alignment in enumerate(allPossibleAlignments[sentence_idx]):
				for word_idx, spanish_word in enumerate(sentence['spanish']):
					english_word_aligned_to_this = sentence['english'][alignment[word_idx]]
					self.translationProbabilities[spanish_word][english_word_aligned_to_this] += probabilitesForEachAlignment[sentence_idx][alignment_idx]

		# Normalize probabilities for each word
		for spanish_word in self.translationProbabilities:
			total_sum = 0
			for eng_word in self.translationProbabilities[spanish_word]:
				total_sum += self.translationProbabilities[spanish_word][eng_word]

			for eng_word in self.translationProbabilities[spanish_word]:
				self.translationProbabilities[spanish_word][eng_word] /= total_sum

	def bestTranslationHasConverged(newBestTranslationForEachWord, oldBestTranslationForEachWord):
		for spanish_word in newBestTranslationForEachWord:
			if newBestTranslationForEachWord[spanish_word] is not oldBestTranslationForEachWord[spanish_word]:
				return False
		return True

if __name__ == '__main__':
	x = ExpectationMaximization('es-en/dev/newstest2012.es', 'es-en/dev/newstest2012.en')
