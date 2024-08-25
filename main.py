from fastapi import FastAPI, Form, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import binascii
import logging
from QuestionDataObject import questionDataObject
import uvicorn
import json

from frenchQuizzGen import frenchQuizzGen
from vocabfr import masterDictionary, totalWordCount, verbs
from starsessions import SessionMiddleware, InMemoryStore, load_session

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
totalQA = 0


# Function to prepare splash page content
def prepareSplash(splashTemplate):

    marker = "<!–– INSERT CATEGORY ––>"
    index = splashTemplate.find(marker)
    if index > 0:
        index -= 2
        topPage = splashTemplate[:index]
        bottomPage = splashTemplate[index:]
        topPage += f'\n<label><input type="radio" name="category" value="ALL" checked>ALL - ({totalWordCount} words)</label>'
        catList = list(masterDictionary.keys())
        # remove all the verbs from the this list
        for v in verbs:
            if v not in catList:
                logger.error(f"Cannot find verb {v} in the category list {catList}")
            else:
                catList.remove(v)
        catList.sort()
        for category in catList:
            topPage += f'\n<label><input type="radio" name="category" value="{category}">{category} - ({len(masterDictionary[category])} words)</label>'
        topPage += '\n <div style="text-align: center; color: red; font-size: 24px;"><br>Verbs<br><br></div>'

        for category in verbs:
            topPage += f'\n<label><input type="radio" name="category" value="{category}">{category} - ({len(masterDictionary[category])} words)</label>'

        wholePage  = topPage+bottomPage

        return wholePage

    return splashTemplate

try:
    with open("frenchpage.html", "r") as file:
        htmltemplate = file.read()
except FileNotFoundError as fex:
    logger.error("Could not load template file - check path")
    htmltemplate = "None - No page loaded "

try:
    with open("splash.html", "r") as file:
        splashPageTemplate = file.read()
        splashPage = prepareSplash(splashPageTemplate)
except FileNotFoundError as fex:
    logger.error("Could not load template file - check path")
    splashPage = "None - No page loaded "

# Initialize FastAPI app
app = FastAPI()

# Configure starsessions with InMemoryStore
secret_key = binascii.hexlify(os.urandom(24)).decode()

store = InMemoryStore()

app.add_middleware(
    SessionMiddleware,
    store=store,
    cookie_name="session",
    cookie_https_only=False
)


async def get_session_data(request: Request) -> questionDataObject:
    # Ensure session is loaded
    await load_session(request)
    if not hasattr(request, 'session'):
        raise RuntimeError("SessionMiddleware is not set up correctly, or session is accessed too early.")

    session_data = request.session.get('data', {})
    #logger.info(f"-------Loading Session data as ----- {session_data}")
    return questionDataObject.from_dict(session_data)
async def set_session_data(request: Request, obj: questionDataObject):
    await load_session(request)
    serialized = obj.to_dict()
    #logger.info(f"*****< storing session as **** {serialized}")
    request.session['data'] = serialized

# Global counter (if needed)
counter = 0


# Endpoint to handle form submission - of the user choice of the type of questions
@app.post("/questions", response_class=HTMLResponse)
async def handle_questions(
    request: Request,
    language: str = Form(...),
    type: str = Form(...),
    category: str = Form(...),
    batch_size: int = Form(30),
    repeat_times: int = Form(3)
):
    page = {
        "language": language,
        "type": type,
        "category": category,
        "batch_size": str(batch_size),
        "repeat": str(repeat_times)
    }
    logger.info(f"Params posted are {page}")
    languageCode = "FRE" if language == "fr_to_en" else "ENG"

    if type == "true_random":
        newURL = f"/random/{languageCode}?filter={category}"
    else:
        qDO = questionDataObject()
        qDO.noBatchRepeats = repeat_times
        qDO.batchSize = batch_size
        frenchQuizz = frenchQuizzGen(qDO)
        frenchQuizz.newBatch(category, qDO)  # Generate a new batch of questions - and update the QDO object
        logger.info(f"Creating a new batch of words - and storing the batch inside the session:")
        await set_session_data(request, qDO)
        newURL = f"/batch/{languageCode}?filter={category}"

    return RedirectResponse(url=newURL, status_code=303)

@app.get("/batch/{language}", response_class=HTMLResponse)
async def batchMode(request: Request, language: str, filter: str = Query(None)):
    global totalQA
    page = htmltemplate
    totalQA +=1

    await load_session(request)

    if "data" in request.session:
        qDO = await get_session_data(request)
        logger.info("Retrieving current state from session")
        counter = int(request.session.get("counter", 0))
    else:
        logger.warning("Session was no longer valid, going to home page")
        return RedirectResponse(url="/", status_code=303)

    if filter is None:
        filter = "ALL"

    logger.info(f"Batch mode, requested language is {language}, batchSize is {qDO.batchSize}, repeats {qDO.noBatchRepeats}")
    if language not in [frenchQuizzGen.ENGLISH, frenchQuizzGen.FRENCH]:
        logger.warning("Unrecognized language, setting to French")
        language = frenchQuizzGen.FRENCH

    frenchQuizz = frenchQuizzGen(qDO)
    question, answer = frenchQuizz.nextQuestionFromBatch(language, filter)
    counter += 1
    questionsLeft = qDO.wordsInBatch + 1
    iteration = 1 + qDO.noBatchRepeats - qDO.repeatBatchCount

    request.session["counter"] = counter
    await set_session_data(request, qDO)
    page = page.replace("#QUESTION", question).replace("#ANSWER", answer).replace("#QNO", "").replace("#MODE", f"Batch Mode - {questionsLeft} questions left, iteration {iteration}, total questions asked {counter}")

    return HTMLResponse(content=page)

@app.get("/random/{language}", response_class=HTMLResponse)
async def randomQuizz(request: Request, language: str, filter: str = Query(None)):
    global totalQA

    totalQA +=1
    page = htmltemplate

    await load_session(request)

    if "data" in request.session:
        qDO = await get_session_data(request)
        frenchQuizz = frenchQuizzGen(qDO)
        logger.info("Retrieving current state from session")
        counter = int(request.session.get("counter", 0))
    else:
        logger.warning("****Session was no longer valid, going to home page****")
        return RedirectResponse(url="/", status_code=303)

    if filter is None:
        filter = "ALL"

    logger.info(f"Random mode, requested language is {language}")
    if language not in [frenchQuizzGen.ENGLISH, frenchQuizzGen.FRENCH]:
        logger.warning("Unrecognized language, setting to French")
        language = frenchQuizzGen.FRENCH

    question, answer = frenchQuizz.nextQuestion(language, filter)
    questionLeft = len(qDO.workingSet)
    size = totalWordCount if filter == frenchQuizz.ALL else len(masterDictionary[filter])
    mode = f"Category {filter} (size {size}) - {questionLeft} questions left"

    logger.info("/random : updating session after question selected")
    counter += 1
    request.session["counter"] = counter
    await set_session_data(request, qDO)
    page = page.replace("#QUESTION", question).replace("#ANSWER", answer).replace("#QNO", str(counter)).replace("#MODE", mode)

    return HTMLResponse(content=page)

# Get the splash - page and create a session if required
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    global  totalQA
    page = splashPage

    await load_session(request)

    if "data" not in request.session:
        logger.info("No Session detected - creating a new one")
        request.session["counter"] = 0

        qDo = questionDataObject()
        await set_session_data(request, qDo)
    else:
        logger.info("Session was found")

    page = page.replace("#QA", str(totalQA))

    return HTMLResponse(content=page)

if __name__ == "__main__":
    # Load HTML templates

    uvicorn.run(app, host="0.0.0.0", port=80)
