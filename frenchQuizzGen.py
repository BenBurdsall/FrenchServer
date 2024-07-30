from vocabfr import totalFreToEng, freToEngVerbs
import logging
import random

class frenchQuizzGen:

    ENGLISH = "ENG"
    FRENCH  = "FRE"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workingSet = totalFreToEng.copy()
        self.repeatBatch = 1
        self.batchSize = 30
        self.noBatchRepeats = 3
        self.repeatBatchCount = self.noBatchRepeats
        self.workingBatch = []
        self.wordsInBatch  = 0
        self.workingVerbs = freToEngVerbs.copy()


    def genderFormat(self,word):

        if word[-3:]==' le':
            word = "le " + word[0:-3]
        else:

            if word[-3:]==' la':
                word = "la " + word[0:-3]
            else:

                if word[-3:]==" l’":
                    word = "l’ " + word[0:-3]
        return word

    # Creates a new batch of cards from the total set, set the repeat count back to max
    def newBatch(self):
        self.batch = []
        totalWords = len(self.workingSet)
        self.repeatBatchCount = self.noBatchRepeats
        if totalWords < self.batchSize:
            self.logger.info("Cannot create a complete batch - Run out  of words, reinitialising word list")
            self.workingSet = totalFreToEng.copy()

        # fill up the batch master list with words taking from working list
        for count in range(0,self.batchSize):
            totalWords = len(self.workingSet)
            choiceIndex = random.randint(0, totalWords - 1)
            pair = self.workingSet[choiceIndex]
            self.batch.append(pair)
            self.workingSet.remove(pair)
        self.workingBatch = self.batch.copy()
        self.logger.info(f"A new batch has been created from the remaining working set, consisting of {self.batch}")



    # draws a next qusestion from batch mode - if the working batch is empty it will recycle the batch a fixed number of times
    def nextQuestionFromBatch(self,inLanguage= FRENCH):
        totalWords = len(self.workingBatch)
        batchWords = len(self.batch)
        self.logger.info(f"working batch {totalWords}, main batch {batchWords} ")
        if totalWords == 0:
            self.logger.info("Run out  of words, reinitialising word list for batch")
            self.repeatBatchCount -=1
            if self.repeatBatchCount > 0:
                self.logger.info(f"current batch is finished, repeating, reseting batch to {self.batch}")
                self.workingBatch = self.batch.copy()  # reset the working batch - back the current batch
            else:
                self.logger.info("Run out  of words, creating a new batch")
                self.newBatch()

        tuple = self.nextQuestionGeneric(inLanguage, self.workingBatch)
        self.wordsInBatch = len(self.workingBatch)
        return tuple

    def nextQuestion(self, inLanguage= FRENCH):
        totalWords = len(self.workingSet)
        self.logger.info(f"Number of words in working set is {totalWords}")
        if totalWords == 0:
            self.logger.info("Run out  of words, reinitialising word list")
            self.workingSet = totalFreToEng.copy()
        tuple  =self.nextQuestionGeneric(inLanguage,self.workingSet)
        return tuple
    def nextQuestionVerb(self, inLanguage= FRENCH):
        totalWords = len(self.workingVerbs)
        self.logger.info(f"Number of Verbs in working set is {totalWords}")
        if totalWords == 0:
            self.logger.info("Run out  of Verbs, reinitialising word list")
            self.workingVerbs = freToEngVerbs.copy()
        tuple  =self.nextQuestionGeneric(inLanguage,self.workingVerbs)
        return tuple

    # Gets the next question, in the language specified, returns a tuple of the question and then the answer
    def nextQuestionGeneric(self,inLanguage, dataset):
        totalWords = len(dataset)
        choiceIndex = random.randint(0, totalWords - 1)
        pair = dataset[choiceIndex]
        frenchWord = pair[0]
        englishWord = pair[1]
        dataset.remove(pair)

        if inLanguage == self.ENGLISH:
            displayWord = englishWord

            answerWord = self.genderFormat(frenchWord.lower())
        else:
            displayWord = self.genderFormat(frenchWord.lower())

            answerWord = englishWord.lower()

        self.logger.info(f"Next question in {inLanguage} is {displayWord} the answer is {answerWord}")
        return (displayWord,answerWord)
