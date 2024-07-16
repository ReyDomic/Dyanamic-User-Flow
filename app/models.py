from sqlalchemy import Column, Integer, String, Date
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    mobile_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    hashtag = Column(String, nullable=True)
    dob = Column(Date, nullable=True)
