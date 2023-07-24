from RedfinAI.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import JSON, Column, Integer, String

#Inheirits base which allows it to be a table
class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True) #Since prmary key automatically gets iterated
    email = Column(String)
    username = Column(String)
    hashed_pass = Column(String)
    saved = Column(JSON)
    refresh_time= Column(String)
