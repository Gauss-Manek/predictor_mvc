from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

class PredictionInput(BaseModel):
    text: str

class PredictionResponse(BaseModel):
    id: int
    text: str
    sentiment: str
    score: float
    user_id: int
    model_config = {"from_attributes": True}