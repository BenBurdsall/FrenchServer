import  logging
import json
import sys
from pathlib import Path


logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Specify the directory path
directory_path = Path('./dict')

# Get the list of filenames
filenames = [file.name for file in directory_path.iterdir() if file.is_file()]



def findDuplicate(master,slaveOriginal,ignoreFirst = False):
    slave  = slaveOriginal.copy()
    for pair in master:
        count = 0
        duplicate="(none)"
        duplicatePair=[]
        for slavePair in slave:

            if slavePair==pair:
                count += 1
                duplicatePair = pair
                if ignoreFirst==False:
                    logger.warning(f"including first time - duplicate: {duplicatePair[0]} ")
                    slave.remove(duplicatePair)
                elif count>1:
                    logger.warning(f"duplicate: {duplicatePair[0]} count {count}")
                    slave.remove(duplicatePair)
    return slave



def dictToList(dictionary):
    l = []
    counter = 0
    for key in dictionary:

        newList = dictionary[key]
        deduped = findDuplicate(l,newList,False)
        logger.info(f"adding {key} to master list - items {len(deduped)}")
        l = l + deduped
        counter += len(deduped)
    logger.info(f"** All Categories extracted  = {counter} words")
    return l




path = "dict"
logger.info(f"Found the following dictionaries: {filenames}")
masterDictionary = {}
for dictionaryFile in filenames:
    try:
        with open(f"{path}/{dictionaryFile}", "r") as file:
            prefix = dictionaryFile[0:-5]
            logger.info(f"attempting to load  {prefix} ")
            contents = json.load(file)
            lcontents = len(contents)
            deduped  = findDuplicate(contents,contents,True)
            ldeduped = len(deduped)

            masterDictionary[prefix] = deduped
            logger.info(f"loading {prefix} consisting of {ldeduped}")
            if ldeduped != lcontents:
                logger.warning(f"Removed duplicated in {prefix} list size difference = {lcontents-ldeduped}")
    except Exception as fex:
        logger.error("Could not load  file or parse it")
        logger.error(fex)



totalFreToEng =  dictToList(masterDictionary)




logger.info("Scrubbing second time....")
deduplicated = findDuplicate(totalFreToEng,totalFreToEng,True)
logger.info(f"second scrubbed list has {len(deduplicated)} items ")
totalFreToEng = deduplicated
totalWordCount = len(totalFreToEng)
logger.info(f"Total word count {totalWordCount}")