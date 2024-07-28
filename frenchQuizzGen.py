from vocabfr import totalFreToEng
import logging
import random

class frenchQuizzGen:

    ENGLISH = "ENG"
    FRENCH  = "FRE"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workingSet = totalFreToEng


    def genderFormat(self,word):
        index = word.find(' le')
        if index > 1:
            word = "le " + word[0:index]
        else:
            index =word.find(' la')
            if index > 1:
                word = "la " + word[0:index]
            else:
                index = word.find(" l'")
                if index > 1:
                    word = "l' " + word[0:index]
        return word



    # Gets the next question, in the language specified, returns a tuple of the question and then the answer
    def nextQuestion(self,inLanguage = FRENCH):
        totalWords = len(self.workingSet)
        if totalWords ==0:
            self.logger.info("Run out  of words, reinitialising word list")
            self.workingSet = totalFreToEng

        choiceIndex = random.randint(0, totalWords - 1)
        pair = self.workingSet[choiceIndex]
        frenchWord = pair[0]
        englishWord = pair[1]
        self.workingSet.remove(pair)

        if inLanguage == self.ENGLISH:
            displayWord = englishWord

            answerWord = self.genderFormat(frenchWord.lower())
        else:
            displayWord = self.genderFormat(frenchWord.lower())

            answerWord = englishWord.lower()

        self.logger.info(f"Next question in {inLanguage} is {displayWord} the answer is {answerWord}")
        return (displayWord,answerWord)
