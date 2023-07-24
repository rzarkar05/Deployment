from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import RedfinAI.models
from RedfinAI.database import engine
from RedfinAI.routers import auth, users, filters
from starlette.staticfiles import StaticFiles

router = APIRouter(
    prefix = '/RedfinAI',
    tags = ['redAI']
)
#
RedfinAI.models.Base.metadata.create_all(bind=engine)

router.mount("/RedfinAI/static", StaticFiles(directory="RedfinAI/static"), name="static")

#Includes prompts recieved from router in auth.py file
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(filters.router)