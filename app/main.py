from typing import List
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Path, Body
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
from .email_utils import send_email
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Management API",
    description="API for managing users across different projects",
    version="1.0.0"
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/add_user", response_model=schemas.UserResponse, responses={422: {"model": schemas.HTTPValidationError}})
def add_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(user=user, db=db)

@app.get("/get_users", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

@app.get("/get_user/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int = Path(..., title="User Id"), db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/update_user/{user_id}", response_model=schemas.UserResponse, responses={422: {"model": schemas.HTTPValidationError}})
def update_user(user_id: int = Path(..., title="User Id"), user: schemas.UserUpdate = Body(...), db: Session = Depends(get_db)):
    updated_user = crud.update_user(db=db, user_id=user_id, user=user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/delete_user/{user_id}", responses={200: {"description": "Successful Response"}, 422: {"model": schemas.HTTPValidationError}})
def delete_user(user_id: int = Path(..., title="User Id"), db: Session = Depends(get_db)):
    crud.delete_user(db=db, user_id=user_id)
    return {"message": "User deleted successfully"}

@app.post("/send_invitation")
def send_invitation(background_tasks: BackgroundTasks):
    recipients = ["shraddha@aviato.consulting"]
    subject = "API Documentation Invitation"
    body = """
    <html>
    <body>
    <h3>Hello,</h3>
    <p>We are excited to invite you to view our User Management API documentation on ReDoc.</p>
    <p>You can access the documentation by clicking the button below:</p>
    <a href="http://52.66.43.178:8000/redoc" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px;">View API Documentation</a>
    <p>We appreciate your time and look forward to your feedback.</p>
    </body>
    </html>
    """

    for recipient in recipients:
        background_tasks.add_task(send_email, recipient, subject, body)

    return {"message": "Invitation emails sent successfully"}
