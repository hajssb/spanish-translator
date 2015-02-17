import sys
import os.path as op

def unicount(sent):
	res = dict()
	for word in sent:
		if word in res:
			res[word] += 1
		else:
			res[word] = 1
	return res

def bicount(sent):
	res = dict()
	count = 0
	if len(sent) <= 1:
		return res, count

	for i in xrange(len(sent)-1):
		bigram = sent[i] + " " + sent[i+1]
		if bigram in res:
			res[bigram] += 1
		else:
			res[bigram] = 1

	return res

def bleu_for_one(ref, evl):
	ref_unigrams = ref.split()
	eval_unigrams = evl.split()

	ref_unicount = unicount(ref)
	eval_unicount = unicount(evl)
	ref_bicount = bicount(ref)
	eval_bicount = bicount(evl)

	N = len(evl)

	unicorrect = 0
	bicorrect = 0

	for unigram in eval_unicount:
		if unigram in ref_unicount:
			unicorrect += min(eval_unicount[unigram], ref_unicount[unigram])

	for bigram in eval_bicount:
		if bigram in ref_bicount:
			bicorrect += min(eval_bicount[bigram], ref_bicount[bigram])

	return 100.0 * unicorrect / N, 100.0 * bicorrect / (N-1)

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "Usage: %s reference_file your_output_file" % (__file__)
		sys.exit(0)

	ref_filename = sys.argv[1]
	eval_filename = sys.argv[2]

	if not op.exists(ref_filename):
		print "Reference file '%s' does not exist." % (ref_filename)
		sys.exit(0)

	if not op.exists(eval_filename):
		print "Output file '%s' does not exist." % (eval_filename)
		sys.exit(0)

	with open(ref_filename) as f_ref:
		with open(eval_filename) as f_eval:
			n_sent = 0
			bleu1 = 0.0
			bleu2 = 0.0
			for ref_line in f_ref:
				eval_line = f_eval.readline()
				if len(eval_line) == 0:
					print "Error: The output file should at least have the same number of sentences as the reference file."
					sys.exit(0)
				t1, t2 = bleu_for_one(ref_line, eval_line)
				bleu1 += t1
				bleu2 += t2
				n_sent += 1

	print "%d sentences evaluated.\nBLEU-1 score: %3.6f\nBLEU-2 score: %3.6f" \
		% (n_sent, bleu1 / n_sent, bleu2 / n_sent)

