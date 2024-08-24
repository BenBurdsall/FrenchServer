from fastapi import FastAPI, Form, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import os
import binascii
import logging
from QuestionDataObject import questionDataObject
import uvicorn
import json

from frenchQuizzGen import frenchQuizzGen
from vocabfr import masterDictionary, totalWordCount
from starsessions import SessionMiddleware, InMemoryStore, load_session

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define the model for form data
class FormData(BaseModel):
    language: str
    type: str
    category: str
    batch_size: int
    repeat_times: int

# Initialize FastAPI app
app = FastAPI()

# Configure starsessions with InMemoryStore
secret_key = binascii.hexlify(os.urandom(24)).decode()

store = InMemoryStore()

app.add_middleware(
    SessionMiddleware,
    store=store,
    cookie_name="session"
)


async def get_session_data(request: Request) -> questionDataObject:
    # Ensure session is loaded
    await load_session(request)
    if not hasattr(request, 'session'):
        raise RuntimeError("SessionMiddleware is not set up correctly, or session is accessed too early.")

    session_data = request.session.get('data', {})
    logger.info(f"-------Loading Session data as ----- {session_data}")
    return questionDataObject.from_dict(session_data)
async def set_session_data(request: Request, obj: questionDataObject):
    await load_session(request)
    serialized = obj.to_dict()
    logger.info(f"*****< storing session as **** {serialized}")
    request.session['data'] = serialized

# Global counter (if needed)
counter = 0

# Function to prepare splash page content
def prepareSplash(splashTemplate):
    marker = "<!–– INSERT CATEGORY ––>"
    index = splashTemplate.find(marker)
    if index > 0:
        index -= 2
        topPage = splashTemplate[:index]
        bottomPage = splashTemplate[index:]
        topPage += f'\n<label><input type="radio" name="category" value="ALL" checked>ALL - ({totalWordCount} words)</label>'
        for category in masterDictionary.keys():
            topPage += f'\n<label><input type="radio" name="category" value="{category}">{category} - ({len(masterDictionary[category])} words)</label>'
        return topPage + bottomPage
    return splashTemplate

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
    languageCode = "ENG" if language == "fr_to_en" else "FRE"

    if type == "true_random":
        newURL = f"/random/{languageCode}?filter={category}"
    else:
        qDO = questionDataObject()
        qDO.noBatchRepeats = repeat_times
        qDO.batchSize = batch_size
        frenchQuizz = frenchQuizzGen(qDO)
        frenchQuizz.newBatch(category, qDO)  # Generate a new batch of questions - and update the QDO object
        logger.info(f"Creating a new batch of words - and storing the batch inside the session: {qDO}")
        await set_session_data(request, qDO)
        newURL = f"/batch/{languageCode}?filter={category}"

    return RedirectResponse(url=newURL, status_code=303)

@app.get("/batch/{language}", response_class=HTMLResponse)
async def batchMode(request: Request, language: str, filter: str = Query(None)):
    page = htmltemplate

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
    page = htmltemplate

    await load_session(request)

    if "data" in request.session:
        qDO = await get_session_data(request)
        frenchQuizz = frenchQuizzGen(qDO)
        logger.info("Retrieving current state from session")
        counter = int(request.session.get("counter", 0))
    else:
        logger.warning("Session was no longer valid, going to home page")
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
    page = splashPage

    await load_session(request)

    if "data" not in request.session:
        logger.info("No Session detected - creating a new one")
        request.session["counter"] = 0

        qDo = questionDataObject()
        await set_session_data(request, qDo)
    else:
        logger.info("Session was found")

    return HTMLResponse(content=page)

if __name__ == "__main__":
    # Load HTML templates
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

    uvicorn.run(app, host="0.0.0.0", port=80)
