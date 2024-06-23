import asyncio
from fastapi import FastAPI, Depends, HTTPException, Form
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from datetime import date
import uvicorn


# SQLAlchemy database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./signup_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define database model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, index=True)
    company_name = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    mobile_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    hashtag = Column(String, nullable=True)
    dob = Column(Date, nullable=True)

# Create database tables
Base.metadata.create_all(bind=engine)

# FastAPI application setup
app = FastAPI()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email_here"
SMTP_PASSWORD = "your_password_here"

# Email sending function
def send_email(to_email: str, subject: str, body: str):
    sender_email = "your_email_here"  # Replace with your sender email
    sender_password = "your_password_here"  # Replace with your app-specific password
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Error sending email")

# Pydantic models
class ProjectForm1(BaseModel):
    company_name: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class ProjectForm2(BaseModel):
    mobile_number: str
    hashtag: str
    first_name: str
    last_name: str

class ProjectForm3(BaseModel):
    mobile_number: str
    first_name: str
    last_name: str
    dob: date

# CRUD operations
@app.post("/add_user")
async def create_user(
    project_id: str = Form(...),
    company_name: str = Form(None),
    first_name: str = Form(...),
    last_name: str = Form(...),
    mobile_number: str = Form(None),
    email: EmailStr = Form(None),
    password: str = Form(None),
    hashtag: str = Form(None),
    dob: date = Form(None),
    db: Session = Depends(get_db)
):
    if project_id == "project_form_1":
        if not all([company_name, email, password]):
            raise HTTPException(status_code=400, detail="Missing project form 1 fields")
        project_data = ProjectForm1(company_name=company_name, first_name=first_name, last_name=last_name, email=email, password=password)
    elif project_id == "project_form_2":
        if not all([mobile_number, hashtag]):
            raise HTTPException(status_code=400, detail="Missing project form 2 fields")
        project_data = ProjectForm2(mobile_number=mobile_number, hashtag=hashtag, first_name=first_name, last_name=last_name)
    elif project_id == "project_form_3":
        if not all([mobile_number, dob]):
            raise HTTPException(status_code=400, detail="Missing project form 3 fields")
        project_data = ProjectForm3(mobile_number=mobile_number, first_name=first_name, last_name=last_name, dob=dob)
    else:
        raise HTTPException(status_code=400, detail="Invalid project ID")

    user = User(project_id=project_id, **project_data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User added successfully", "user_id": user.id, "user_data": user}

@app.get("/get_user/{user_id}")
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/get_users")
async def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.put("/update_user/{user_id}")
async def modify_user(
    user_id: int,
    project_id: str = Form(...),
    company_name: str = Form(None),
    first_name: str = Form(...),
    last_name: str = Form(...),
    mobile_number: str = Form(None),
    email: EmailStr = Form(None),
    password: str = Form(None),
    hashtag: str = Form(None),
    dob: date = Form(None),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if project_id == "project_form_1":
        if not all([company_name, email, password]):
            raise HTTPException(status_code=400, detail="Missing project form 1 fields")
        project_data = ProjectForm1(company_name=company_name, first_name=first_name, last_name=last_name, email=email, password=password)
    elif project_id == "project_form_2":
        if not all([mobile_number, hashtag]):
            raise HTTPException(status_code=400, detail="Missing project form 2 fields")
        project_data = ProjectForm2(mobile_number=mobile_number, hashtag=hashtag, first_name=first_name, last_name=last_name)
    elif project_id == "project_form_3":
        if not all([mobile_number, dob]):
            raise HTTPException(status_code=400, detail="Missing project form 3 fields")
        project_data = ProjectForm3(mobile_number=mobile_number, first_name=first_name, last_name=last_name, dob=dob)
    else:
        raise HTTPException(status_code=400, detail="Invalid project ID")

    for key, value in project_data.dict().items():
        setattr(user, key, value)
    user.project_id = project_id
    db.commit()
    db.refresh(user)
    return {"message": "User updated successfully", "user_id": user.id, "user_data": user}

@app.delete("/delete_users/{user_id}")
async def remove_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully", "user_id": user.id}

@app.post("/send-invitation/")
async def send_invitation(
    to_email: str = Form(...),
):
    subject = "Invitation to Check API Documentation"
    redoc_url = "http://127.0.0.1:8000/redoc"
    body = f"Hello,\n\nYou are invited to check out our API documentation at the following link:\n\n{redoc_url}\n\nBest regards,\nYour Team"

    send_email(to_email, subject, body)
    return {"message": "Invitation email sent successfully"}

if __name__ == "__main__":
    config = uvicorn.Config(app, host="127.0.0.1", port=8000)
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(server.serve())
    except KeyboardInterrupt:
        loop.run_until_complete(server.shutdown())
        loop.stop()
        loop.close()

