import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from app.database import Base, engine, get_db
from app.models import UserModel, PredictionModel
from app.schemas import UserCreate, UserUpdate, UserResponse, Token, PredictionInput, PredictionResponse
from app.auth import (get_password_hash, verify_password, create_access_token,
                      get_current_user, verify_admin, ACCESS_TOKEN_EXPIRE_MINUTES)
from app.ml import predict_sentiment

# Initialisation des tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Data Science API - Production Ready (Python 3.13)")

# Configuration CORS
ALLOWED_ORIGINS = ["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:8080"]
FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not FRONTEND_URL else ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur indisponible")
    hashed = get_password_hash(user.password)
    new_user = UserModel(username=user.username, hashed_password=hashed, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Identifiants incorrects")
    token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}

@app.put("/users/me", response_model=UserResponse)
def update_profile(profile_data: UserUpdate, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if profile_data.username and profile_data.username != current_user.username:
        existing_user = db.query(UserModel).filter(UserModel.username == profile_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà utilisé")
        current_user.username = profile_data.username
    if profile_data.password:
        current_user.hashed_password = get_password_hash(profile_data.password)
    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/predict", response_model=PredictionResponse)
def run_prediction(payload: PredictionInput, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    prediction_result = predict_sentiment(payload.text)
    db_pred = PredictionModel(
        text=payload.text,
        sentiment=prediction_result["sentiment"],
        score=prediction_result["score"],
        user_id=current_user.id
    )
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)
    return db_pred

@app.get("/admin/history", response_model=List[PredictionResponse])
def view_all_history(admin_user: UserModel = Depends(verify_admin), db: Session = Depends(get_db)):
    return db.query(PredictionModel).all()