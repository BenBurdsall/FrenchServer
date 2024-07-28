from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from frenchQuizzGen import frenchQuizzGen
import logging


frenchQuizz = frenchQuizzGen()
logger = logging.getLogger(__name__)
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


@app.get("/", response_class=HTMLResponse)
def read_root():
    global  counter
    page = htmltemplate
    tuple = frenchQuizz.nextQuestion(frenchQuizzGen.FRENCH)
    question, answer = tuple

    counter = counter + 1
    page = page.replace("#QUESTION",question).replace("#ANSWER",answer).replace("#QNO",str(counter))

    return page



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
