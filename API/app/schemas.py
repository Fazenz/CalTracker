from pydantic import BaseModel, EmailStr
from datetime import date

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class FoodCreate(BaseModel):
    name: str
    calories_100g: float
    protein_100g: float
    carbs_100g: float
    fat_100g: float

class ConsumptionCreate(BaseModel):
    user_id: int
    food_id: int
    quantity: float
    date: date

class PasswordChange(BaseModel):
    old_password: str
    new_password: str