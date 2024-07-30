
from frenchQuizzGen import frenchQuizzGen
import logging
import sys

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

# Define the model for form data
class FormData(BaseModel):
    language: str
    type: str
    batch_size: int
    repeat_times: int

frenchQuizz = frenchQuizzGen()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
app = FastAPI()
counter = 0

# Read the HTML file
logger.info("Tying to access HTML template ")
try:
    with open("frenchpage.html", "r") as file:
        htmltemplate = file.read()
except FileNotFoundError as fex:
    logger.error("Could not load template file - check path")
    htmltemplate = "None - No page loaded "

try:
    with open("splash.html", "r") as file:
        splashPage = file.read()
except FileNotFoundError as fex:
    logger.error("Could not load template file - check path")
    htmltemplate = "None - No page loaded "






# Endpoint to handle form submission
@app.post("/questions")
async def handle_questions(
    language: str = Form(...),
    type: str = Form(...),
    batch_size: int = Form(30),
    repeat_times: int = Form(3)
):

    page = {
    "language" : language,
    "type" : type,
    "batch_size" : str(batch_size),
    "repeat" : str(repeat_times)

    }
    logger.info("Params posted are {page")
    languageCode = "ENG"
    if language=="fr_to_en":
        languageCode = "FRE"

    if type == "true_random":
        newURL = f"/random/{languageCode}"
    elif type=='verbs':
        newURL = f"/random/{languageCode}?filter=verbs"
    else:
        frenchQuizz.noBatchRepeats = repeat_times
        frenchQuizz.batchSize = batch_size
        frenchQuizz.newBatch()
        newURL = f"/batch/{languageCode}"


    return RedirectResponse(url=newURL ,status_code=303)


@app.get("/batch/{language}", response_class=HTMLResponse)
async def batchMode(language : str ):
    global  counter
    page = htmltemplate

    logger.info(f"Batch  mode, requested language is {language}, batchSize is {frenchQuizz.batchSize}, repeats {frenchQuizz.noBatchRepeats} ")
    if language not in [frenchQuizzGen.ENGLISH, frenchQuizzGen.FRENCH]:
        logger.warning("Not recognised langauge - setting to French")
        language = frenchQuizzGen.FRENCH

    tuple = frenchQuizz.nextQuestionFromBatch(language)
    question, answer = tuple

    counter = counter + 1
    questionsLeft  = frenchQuizz.wordsInBatch +1
    iteration = 1+frenchQuizz.noBatchRepeats-frenchQuizz.repeatBatchCount
    page = page.replace("#QUESTION",question).replace("#ANSWER",answer).replace("#QNO","").replace("#MODE",f"Batch Mode - {questionsLeft} questions left, iteration {iteration}")

    return page
@app.get("/random/{language}", response_class=HTMLResponse)
async def randomQuizz(language : str,
                      filter: str = None ):
    global  counter
    page = htmltemplate

    logger.info(f"Random  mode, requested language is {language}")
    if language not in [frenchQuizzGen.ENGLISH, frenchQuizzGen.FRENCH]:
        logger.warning("Not recognised langauge - setting to French")
        language = frenchQuizzGen.FRENCH

    if filter == "verbs":
        logger.info("selecting from verbs only")
        tuple = frenchQuizz.nextQuestionVerb(language)
        mode ="Only Verbs"
    else:
        tuple = frenchQuizz.nextQuestion(language)
        mode = "All words Randomly"
    question, answer = tuple

    counter = counter + 1
    page = page.replace("#QUESTION",question).replace("#ANSWER",answer).replace("#QNO",str(counter)).replace("#MODE",mode)

    return page
@app.get("/", response_class=HTMLResponse)
async def read_root():
    page = splashPage
    return HTMLResponse(content=page)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
