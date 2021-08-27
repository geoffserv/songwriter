# songwriter.py
# Match rhyme and meter between lines of source text to generate song verses

from Phyme import Phyme # pip install phyme
import syllables # pip install syllables
import re
import time
import random

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

sourceFile = "bible_short.txt"

# Some debug counters

debugTotalLinesProcessed = 0 # Including garbage lines discarded during processing
debugTotalWordsProcessed = 0
debugTotalSyllablesSeen = 0 # Total count of every syllable of every word we've seen
debugTotalDiscardedLines = 0 # Discarded dupes, unrhymables, out of meter, etc.  All discarded lines
debugTotalUniqueLines = 0 # Unique lines we've seen
debugTotalUnrhymable = 0 # LastWords encountered which have no data in the rhyme dictionary
debugTotalOutOfMeter = 0 # Lines that don't match our desired meter
debugProcStartTime = 0 # Clocks for tracking execution time
debugProcEndTime = 0

if __name__ == "__main__":

	# Song Building
	# PROOF OF CONCEPT
	# Rhyme and meter scheme:
	# A (approx 9 syllables)
	# B (approx 6 syllables)
	# A (approx 9 syllables)
	# B (approx 6 syllables)

	songMeter = {'A' : 9, 'B' : 6}

	songMeterPadding = 1 # Give or take this many syllables.  The syllable estimator is also kinda inaccurate

	# Set the meter now.  This will save an enormous amount of processing from discarding non-matching lines.

	print("Song Meter- A line:", songMeter['A'], "syllables; B line:", songMeter['B'], "syllables")

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

	debugTotalDiscardedLines = debugTotalLinesSeen - len(sourceSentences)

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

				# Discard all lines that don't match the A or B meter plus-or-minus the meter padding
				if not ( 
             ( (sourceSentenceSyllables < songMeter['A'] + songMeterPadding) and
             (sourceSentenceSyllables > songMeter['A'] - songMeterPadding) ) or
             ( (sourceSentenceSyllables < songMeter['B'] + songMeterPadding) and
             (sourceSentenceSyllables > songMeter['B'] - songMeterPadding) ) ):
					debugTotalOutOfMeter += 1
					debugTotalDiscardedLines += 1
					continue # Move along.  Nothing to see here.

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
						debugTotalDiscardedLines += 1
						continue # Move along.  Nothing to see here.

					newLyric = {
                     lastWord:[
                                 [
                                   [sourceSentence, sourceSentenceSyllables]
                                 ],
                                 [
                                   [sourceSentenceRhymeList1, 0]
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
	print("INFO- Total Discarded lines:", debugTotalDiscardedLines)
	print("INFO- Total Un-Rhymable words:", debugTotalUnrhymable)
	print("INFO- Total Out-Of-Meter lines:", debugTotalOutOfMeter)
	print("INFO- Total Unique lyric lines available:", debugTotalUniqueLines)
	print("INFO- Lyric Dictionary is ready!")

	lyricSearchLimit = 1000 # Search this many times until giving up, otherwise may loop forever.  Gross hack but ok 4now

	currentLine = "A"

	lyricVerse = [] # Store the final chosen verses here

	while ( len(lyricVerse) < 4 ) : # Loop until we have 4 lines

		lyricSearchCount = 0
	
		lyricLine = ""
		rhymeLine = ""
	
		while (not (lyricLine and rhymeLine)): # Loop until we have found viable lyricLine and associated rhymeLine

			lyricSearchCount += 1
			if (lyricSearchCount > lyricSearchLimit):
				print("DEBUG: Reached search limit.  Bye!")
				break

			# Search for a candidate line
			lyricLineCandidates = random.choice(list(lyricDict.items()))
			lyricLineCandidatesInMeter = []
			# [0] = the lastWord
			# [1][0] = the sentence list
			# [1][1] = the rhyme list

			# loop through and find candidates that match this meter
			for lyricLineCandidate in lyricLineCandidates[1][0]:
				if ((lyricLineCandidate[1] > songMeter[currentLine] - songMeterPadding) and (lyricLineCandidate[1] < songMeter[currentLine] + songMeterPadding)):
					# This candidate is in meter, consider it
					lyricLineCandidatesInMeter.append(lyricLineCandidate[0])

			# print("DEBUG - ", currentLine, "line: Considering line candidates:",lyricLineCandidatesInMeter)

			if lyricLineCandidatesInMeter:
				lyricLine = random.choice(lyricLineCandidatesInMeter) # Pick a random candidate lyric line
				lyricLineLastWord = lyricLine.split()[-1]

				candidateRhymeList = [] # We'll store some rhyme candidates in here for choosing

				for candidateRhyme in lyricDict[lyricLineLastWord][1][0][0]: # Loop through each potential rhyme
					if candidateRhyme in lyricDict:
						# print("DEBUG - ", currentLine, "line: - Found rhyme words existing in the lyricDict:", candidateRhyme)
						# Add it to the candidate rhyme word list, unless it's exactly the same word
						if not (candidateRhyme == lyricLineLastWord):
							candidateRhymeList.append(candidateRhyme)

				if candidateRhymeList:
					# Dedup and choose a random potential rhyme word
					chosenRhyme = random.choice(list(dict.fromkeys(candidateRhymeList)))
					# print("DEBUG - ", currentLine, "line: - Chosen rhyme word:",chosenRhyme)

					# Find a list of lines that have the same lastWord that rhymes
					chosenRhymeLyricLineCandidates = lyricDict[chosenRhyme][0]
					# print("DEBUG - ", currentLine, "line: - - Rhyming line candidates:",chosenRhymeLyricLineCandidates)

					chosenRhymeLyricLineCandidatesInMeter = []

					# loop through and find candidate lines that match this meter
					for chosenRhymeLyricLineCandidate in chosenRhymeLyricLineCandidates:
						if ((chosenRhymeLyricLineCandidate[1] > songMeter[currentLine] - songMeterPadding) and (chosenRhymeLyricLineCandidate[1] < songMeter[currentLine] + songMeterPadding)):
							# Add them to the candidate list unless they're exactly the same line
							if not (chosenRhymeLyricLineCandidate[0] == lyricLine) :
								chosenRhymeLyricLineCandidatesInMeter.append(chosenRhymeLyricLineCandidate[0])

					if chosenRhymeLyricLineCandidatesInMeter:
						rhymeLine = random.choice(chosenRhymeLyricLineCandidatesInMeter)

		lyricVerse.append(lyricLine)
		lyricVerse.append(rhymeLine)

		if (currentLine == "A"): currentLine = "B"
		else: currentLine = "A"

	Verse = [lyricVerse[0], lyricVerse[2], lyricVerse[1], lyricVerse[3]] # Put it in ABAB

	print(Verse)
