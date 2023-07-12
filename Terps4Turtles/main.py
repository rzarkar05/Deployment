from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import Terps4Turtles.models
from Terps4Turtles.database import engine
from Terps4Turtles.routers import auth, map, users
from starlette.staticfiles import StaticFiles

router = APIRouter(
    prefix = '/terps4turtles',
    tags = ['t4t']
)
#
Terps4Turtles.models.Base.metadata.create_all(bind=engine)

router.mount("/Terps4Turtles/static", StaticFiles(directory="Terps4Turtles/static"), name="static")

#Includes prompts recieved from router in auth.py file
router.include_router(auth.router)
router.include_router(map.router)
router.include_router(users.router)