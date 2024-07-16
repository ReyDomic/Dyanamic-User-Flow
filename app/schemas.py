from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import date

class ValidationError(BaseModel):
    loc: List[Any]
    msg: str
    type: str

class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = None
    
class UserCreate(BaseModel):

    company_name: Optional[str] = None
    first_name: str
    last_name: str
    mobile_number: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    hashtag: Optional[str] = None
    dob: Optional[date] = None

class UserUpdate(BaseModel):
    id: int
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    hashtag: Optional[str] = None
    dob: Optional[date] = None

class UserResponse(BaseModel):
    id: int
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    hashtag: Optional[str] = None
    dob: Optional[date] = None

    class Config:
        from_attributes = True
        
        
