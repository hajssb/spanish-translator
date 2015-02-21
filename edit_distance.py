alphabet = "abcdefghijklmnopqrstuvwxyz"

def generate_all_insertions(word):
	all_words = []
	for i in range(0,len(word)+1):
		for char in alphabet:
			all_words.append(word[:i] + char + word[i:])
	return all_words

def generate_all_deletions(word):
	all_words = []
	for i in range(1,len(word)+1):
		all_words.append(word[:i-1] + word[i:])
	return all_words

def generate_all_replacements(word):
	all_words = []
	for i in range(1,len(word)+1):
		for char in alphabet:
			all_words.append(word[:i-1] +char+ word[i:])
	return all_words

def generate_all_one_edit(word):
	all_words = []
	insertions = generate_all_insertions(word)
	all_words.extend(insertions)

	deletions = generate_all_deletions(word)
	all_words.extend(deletions)

	replacements = generate_all_replacements(word)
	all_words.extend(replacements)

	return all_words

if __name__ == '__main__':
	generate_all_one_edit("marcel")


