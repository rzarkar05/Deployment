from fastapi import FastAPI
from urllib3 import HTTPResponse
import AsterApp.models
from AsterApp.database import engine
from AsterApp.routers import auth, todos, users, finances
import AINFL.main
import Terps4Turtles.main 
import RedfinAI.main
from starlette.staticfiles import StaticFiles
import EmailAnalyzer.processor
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
import warnings
warnings.filterwarnings("ignore")

app = FastAPI()


AsterApp.models.Base.metadata.create_all(bind=engine)
app.mount("/AsterApp/static", StaticFiles(directory="AsterApp/static"), name="static")
app.mount("/EmailAnalyzer/resources", StaticFiles(directory="EmailAnalyzer/resources"), name="resources")
app.mount("/AINFL/static", StaticFiles(directory="AINFL/static"), name="static")
app.mount("/Portfolio", StaticFiles(directory="Portfolio"), name="static")
app.mount("/Terps4Turtles/static", StaticFiles(directory="Terps4Turtles/static"), name="static")
app.mount("/RedfinAI/static", StaticFiles(directory="RedfinAI/static"), name="static")

#ASTER APP 
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
app.include_router(finances.router)


#EMAIL ANALYZER
templatesEmailAnalyzer =  Jinja2Templates(directory="EmailAnalyzer/templates")
df = EmailAnalyzer.processor.display('raw',EmailAnalyzer.processor.create_df('default'))
@app.get("/nlp-email-analyzer/{type}", response_class=HTMLResponse)
async def display(request:Request, type: str):
    df = EmailAnalyzer.processor.display(type,EmailAnalyzer.processor.create_df('default'))
    if type == 'images':
        return templatesEmailAnalyzer.TemplateResponse("images.html", {"request": request})
    return templatesEmailAnalyzer.TemplateResponse("index.html", {"request": request, "df":df})

#AI NFL
app.include_router(AINFL.main.router)

#PORTFOLIO
templates = Jinja2Templates(directory="Portfolio")
@app.get("/portfolio", response_class=HTTPResponse)
async def portfolio(request:Request):
    return templates.TemplateResponse("personalPortfolio.html", {"request": request})

#TERPS4TURTLES
app.include_router(Terps4Turtles.main.router)

#TERPS4TURTLES
app.include_router(RedfinAI.main.router)