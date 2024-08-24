from vocabfr import totalFreToEng, masterDictionary
import logging
import random
from QuestionDataObject import questionDataObject

class frenchQuizzGen:

    ENGLISH = "ENG"
    FRENCH  = "FRE"
    ALL = "ALL"

    def __init__(self, qDO : questionDataObject):
        self.logger = logging.getLogger(__name__)
        self.questionDO = qDO


    # Sets the Data conte

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

    # Creates a new batch of cards from the total set, set the repeat count back to max - updates the questionDataObject passed
    def newBatch(self,filter,qDO : questionDataObject):
        qDO.batch = []
        totalWords = len(qDO.workingSet)
        qDO.repeatBatchCount = qDO.noBatchRepeats
        if totalWords < qDO.batchSize:
            self.logger.info("Cannot create a complete batch - Run out  of words, reinitialising word list")
            if filter== frenchQuizzGen.ALL:
                self.logger.info("Combining all categories")
                qDO.workingSet = totalFreToEng.copy()
            else:
                self.logger.info(f"Setting category to {filter}")
                qDO.workingSet = masterDictionary[filter].copy()

        # fill up the batch master list with words taking from working list
        for count in range(0,qDO.batchSize):
            totalWords = len(qDO.workingSet)
            choiceIndex = random.randint(0, totalWords - 1)
            pair =qDO.workingSet[choiceIndex]
            qDO.batch.append(pair)
            qDO.workingSet.remove(pair)
            if len(qDO.workingSet) == 0:
                break
        qDO.workingBatch = qDO.batch.copy()
        self.logger.info(f"A new batch has been created from the remaining working set, consisting of {qDO.batch}")



    # draws a next qusestion from batch mode - if the working batch is empty it will recycle the batch a fixed number of times
    def nextQuestionFromBatch(self,inLanguage,filter):
        totalWords = len(self.questionDO.workingBatch)
        batchWords = len(self.questionDO.batch)
        self.logger.info(f"working batch {totalWords}, main batch {batchWords} ")
        if totalWords == 0:
            self.logger.info("Run out  of words, reinitialising word list for batch")
            self.questionDO.repeatBatchCount -=1
            if self.questionDO.repeatBatchCount > 0:
                self.logger.info(f"current batch is finished, repeating, reseting batch to {self.questionDO.batch}")
                self.questionDO.workingBatch = self.questionDO.batch.copy()  # reset the working batch - back the current batch
            else:
                self.logger.info("Run out  of words, creating a new batch")
                self.newBatch(filter.self.questionDO)

        tuple = self.nextQuestionGeneric(inLanguage, self.questionDO.workingBatch)
        self.questionDO.wordsInBatch = len(self.questionDO.workingBatch)
        return tuple

    def nextQuestion(self, inLanguage, filter):
        totalWords = len(self.questionDO.workingSet)
        self.logger.info(f"Number of words in working set is {totalWords}")
        if totalWords == 0:
            self.logger.info("Run out  of words, reinitialising word list")
            if filter== frenchQuizzGen.ALL:
                self.logger.info(f"combining all categories")
                self.questionDO.workingSet = totalFreToEng.copy()
            else:
                self.logger.info(f"Setting category to {filter}")
                self.questionDO.workingSet = masterDictionary[filter].copy()

        tuple  =self.nextQuestionGeneric(inLanguage,self.questionDO.workingSet)
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
