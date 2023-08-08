##IMPORTS
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import update
from RedfinAI.routers.auth import get_curr_user
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Depends, APIRouter, Form, Request, Response
from fastapi import HTTPException
import RedfinAI.models
from RedfinAI.database import SessionLocal, engine
from sqlalchemy.orm import Session
from datetime import datetime
from starlette import status

router = APIRouter(
    prefix = '/filters',
    tags=['filters']
)
templates = Jinja2Templates(directory="RedfinAI/templates")
RedfinAI.models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def filter(df, min_price=0, max_price=9999999, city=None, zipcode=None, house_type=['Townhouse','Single Family Residential','Multi-Family (2-4 Unit)']):
    temp = df
    temp = temp[temp['PROPERTY TYPE'].isin(house_type)]
    if zipcode is not None:
        temp = temp[temp['ZIP OR POSTAL CODE'] == zipcode]
    if city is not None:
        temp = temp[temp['CITY'] == city]
    temp = temp[(temp['PRICE']>=min_price)&(temp['PRICE']<=max_price)]
    return temp

def get_description(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    div_element = soup.find('div', id='marketing-remarks-scroll')
    if div_element:
        print("ELEMENT FOUND... SCRAPING...")
        div_content = div_element.get_text()
        return str(div_content)
    else:
        print("ELEMENT NOT FOUND...")
        return 'None'


def sentiment_analysis(data):
    data = data.rename(columns={'URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)':'URL', 'ZIP OR POSTAL CODE':'ZIPCODE','MLS#':'MLS'})
    data = data.drop(['SALE TYPE','SOLD DATE','$/SQUARE FEET','STATUS','NEXT OPEN HOUSE START TIME','NEXT OPEN HOUSE END TIME','SOURCE','FAVORITE','INTERESTED','LATITUDE','LONGITUDE'], axis=1)
    data['DESCRIPTION'] = data['URL'].apply(get_description)
    keywords_points = {
        'needs work': 2,
        'potential': 1,
        'investor': 2,
        'repair': 1,
        'tlc': 1,
        'shortsale': 2,
        'short sale':2,
        'as-is':1,
        'as is':1,
        'unfinished': 2,
        'un finished': 2,
        'rehab':1
    }
    data['DESCRIPTION'] = data['DESCRIPTION'].str.lower()
    data['POTENTIAL SCORE'] = 0
    for index, row in data.iterrows():
        description = row['DESCRIPTION']
        score = 0
        for keyword, points in keywords_points.items():
            if keyword in description:
                score += points
        data.at[index, 'POTENTIAL SCORE'] = score
    data = data.sort_values(by='POTENTIAL SCORE', ascending=False)
    return data


@router.get("/", response_class=HTMLResponse)
async def filtering(request: Request):
    return templates.TemplateResponse("display.html", {"request": request, "df":None})


@router.post("/", response_class=HTMLResponse)
async def filtering(request: Request, min_price: int = Form(...), max_price: int = Form(...), 
                    Townhouse: bool = Form(False),
                    SingleFamily: bool = Form(False),
                    MultiFamily: bool = Form(False),
                    city: str = Form(None), 
                    zipcode: str = Form(None), db: Session = Depends(get_db)):
    SHEET_ID = '195bxsJd05pT89yx1f2wJkUYPHJfRxvTs0BQrEVxLP68'
    SHEET_NAME = 'Sheet1'
    url = 'https://docs.google.com/spreadsheets/d/195bxsJd05pT89yx1f2wJkUYPHJfRxvTs0BQrEVxLP68/gviz/tq?tqx=out:csv&sheet=Sheet1'
    temp = pd.read_csv(url)
    house_type = []
    if(Townhouse):
        house_type.append('Townhouse')
    if(SingleFamily):
        house_type.append('Single Family Residential')
    if(MultiFamily):
        house_type.append('Multi-Family (2-4 Unit)')
    df= filter(temp, min_price, max_price, city, zipcode, house_type)
    df = sentiment_analysis(df)
    return templates.TemplateResponse("display.html", {"request": request, "df":df})




