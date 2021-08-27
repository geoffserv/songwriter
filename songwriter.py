# songwriter.py
# Match rhyme and meter between lines of source text to generate song verses

from Phyme import Phyme # pip install phyme
import syllables # pip install syllables
import re
import time

# lyricDict will contain a lyric dictionary built from the source text
# The key will be the last word of each line
# The value will be a list:
#   element 0, a list of every line ending in that word
#      element 0, the line text itself
#      element 1, the number of syllables estimated in that line
#   element 1, a list of every known rhyme with that word:
#      element 0, the rhyme word
#      element 1, the type of rhyme:
#                 0 = Perfect rhyme (FOB, DOG)
#                 1 = same vowels and consonants of the same type regardless of voicing (HAWK, DOG)
#                 2 = same vowels and consonants as well as any extra consonants (DUDES, DUES)
#                 3 = same vowels and a subset of the same consonants (DUDE, DO)
#                 4 = same vowels and some of the same consonants, with some swapped for other consonants (FACTOR, FASTER)
#                 5 = same vowels and arbitrary consonants (CASH, CATS)
#                 6 = not the same vowels but the same consonants (CAT, BOT)
#                 so, the higher this index, the less "rhymey" is it, kinda

lyricDict = {}

# Source File contains the text to process

sourceFile = "bible.txt"

# Some debug counters

debugTotalLinesProcessed = 0 # Including garbage lines discarded during processing
debugTotalWordsProcessed = 0
debugTotalSyllablesSeen = 0
debugDiscardedDupes = 0
debugTotalUniqueLines = 0
debugTotalUnrhymable = 0
debugProcStartTime = 0
debugProcEndTime = 0

if __name__ == "__main__":

	debugProcStartTime = time.time()

	rhyme = Phyme()

	print("INFO- Opening file for processing:", sourceFile)

	# Read the entire source file in to a string for later splitting and manipulation
	# This is very inefficient but hello-world quality for now
	# Read in and kill the newlines because they're unimportant
	sourceTextFile = open(sourceFile, 'r') # some public domain text as a test case
	sourceTextBlob = sourceTextFile.read().replace('\n', ' ')
	sourceTextFile.close()

	sourceSentences = re.split('[,.!]', sourceTextBlob) # Break it apart at every comma,period,ep

	debugTotalLinesSeen = len(sourceSentences)

	print("INFO- Deduplicating sentence list ...")
	sourceSentences = list(dict.fromkeys(sourceSentences))

	debugDiscardedDupes = debugTotalLinesSeen - len(sourceSentences)

	print("INFO- Building lyric dictionary ...")
	
	for sourceSentence in sourceSentences:

			debugTotalLinesProcessed += 1

			if len(sourceSentence) > 1: # Empty elements get caught up in here and crash, look for >1 element sentences only

				sourceSentence = sourceSentence.strip()
				sourceSentenceWords = sourceSentence.split()
				lastWord = sourceSentenceWords[-1]

				debugTotalWordsProcessed += len(sourceSentenceWords)

				# Sentence Syllable Estimation
				# Can only estimate syllable count per-word, so run the estimator on every word in the sentence and accumulate
				sourceSentenceSyllables = 0
				for sourceSentenceWord in sourceSentenceWords:
					sourceSentenceSyllables += syllables.estimate(sourceSentenceWord)
					debugTotalSyllablesSeen += sourceSentenceSyllables


				if not lastWord in lyricDict:
					# Haven't encountered this last word before, so build a lyricDict entry for this last word

					# LastWord rhyme lookups
					# Do the rhyme calculations here, only needed once per lastWord
					# Phyme will throw a KeyError if it can't find corresponding rhymes
					try:
						# What comes back is a dictionary of syllable counts with corresponding lists of rhyme words.
						# Kinda don't care about rhyme word syllable counts right now, so just collapse this to values() only
						sourceSentenceRhymeList1 = rhyme.get_perfect_rhymes(lastWord).values()
						# Now this is a list of lists, better to collapse to a single list of all the words
						sourceSentenceRhymeList1 = [item for sublist in sourceSentenceRhymeList1 for item in sublist]
						# Maybe someday do fancy things with lastWord syllable count ...

					except KeyError:
						# Can't find any rhyming words in the dictionary, so just discard this entirely and move along
						debugTotalUnrhymable += 1
						continue # Move along.  Nothing to see here.

					newLyric = {lastWord:[
                                 [
                                   [sourceSentence, sourceSentenceSyllables]
                                 ]
                               ]
                     }
					lyricDict.update(newLyric)
					debugTotalUniqueLines += 1

				else:
					# This last word has already been catalogued, so add this new sentence to the dictionary entry
					lyricDict[lastWord][0].append([sourceSentence, sourceSentenceSyllables])
					debugTotalUniqueLines += 1
	
	debugProcEndTime = time.time()
	print("INFO- Completed building lyric dictionary in", debugProcEndTime-debugProcStartTime, "seconds")
	print("INFO- Total Lines Processed:", debugTotalLinesProcessed)
	print("INFO- Total Words Processed:", debugTotalWordsProcessed)
	print("INFO- Total Syllables seen:", debugTotalSyllablesSeen)
	print("INFO- Total Discarded duplicate lines:", debugDiscardedDupes)
	print("INFO- Total Un-Rhymable words encountered:", debugTotalUnrhymable)
	print("INFO- Total Unique lyric lines available:", debugTotalUniqueLines)
