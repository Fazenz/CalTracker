from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .models import User, Food, Consumption
from .schemas import UserCreate, FoodCreate, ConsumptionCreate, PasswordChange
from passlib.context import CryptContext
from datetime import date, datetime, timedelta
from .auth import verify_password, create_access_token, decode_access_token

# Hasher les mots de passe
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Créer l'app FastAPI
app = FastAPI(
    title="CalTracker API",
    description="API pour suivre les apports alimentaires et la consommation de chaque utilisateur.",
    version="1.0.0",
    docs_url="/docs",         # Swagger disabled
    redoc_url="/redocs"      # ReDoc at /docs
)

# Crée toutes les tables dans la base de données
Base.metadata.create_all(bind=engine)

# Dépendance pour obtenir une session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Récupérer l'utilisateur courant à partir du token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

#Routes GET
# Route racine
@app.get("/", tags=["Root"])
def root():
    return {"message": "CalTracker API running"}

# Route pour calculer les apports d'un jour
@app.get("/stats/day", tags=["GET Methods"])
def daily_stats(user_id: int = Query(...), day: date = Query(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access stats for another user")
    consumptions = db.query(Consumption).filter(
        Consumption.user_id == user_id,
        Consumption.date == day
    ).all()
    total_calories = total_protein = total_carbs = total_fat = 0
    for c in consumptions:
        total_calories += (c.food.calories_100g * c.quantity / 100)
        total_protein  += (c.food.protein_100g * c.quantity / 100)
        total_carbs    += (c.food.carbs_100g * c.quantity / 100)
        total_fat      += (c.food.fat_100g * c.quantity / 100)
    return {
        "date": str(day),
        "user_id": user_id,
        "calories": total_calories,
        "protein": total_protein,
        "carbs": total_carbs,
        "fat": total_fat
    }

# Routes pour des stats hebdomadaires
@app.get("/stats/week", tags=["GET Methods"])
def weekly_stats(user_id: int = Query(...), start_day: date = Query(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access stats for another user")
    end_day = start_day + timedelta(days=6)
    consumptions = db.query(Consumption).filter(
        Consumption.user_id == user_id,
        Consumption.date >= start_day,
        Consumption.date <= end_day
    ).all()
    total_calories = total_protein = total_carbs = total_fat = 0
    for c in consumptions:
        total_calories += (c.food.calories_100g * c.quantity / 100)
        total_protein  += (c.food.protein_100g * c.quantity / 100)
        total_carbs    += (c.food.carbs_100g * c.quantity / 100)
        total_fat      += (c.food.fat_100g * c.quantity / 100)
    return {
        "week_start": str(start_day),
        "week_end": str(end_day),
        "user_id": user_id,
        "calories": total_calories,
        "protein": total_protein,
        "carbs": total_carbs,
        "fat": total_fat
    }

# Routes pour des stats mensuelles
@app.get("/stats/month", tags=["GET Methods"])
def monthly_stats(user_id: int = Query(...), start_day: date = Query(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access stats for another user")
    end_day = start_day + timedelta(days=29)
    consumptions = db.query(Consumption).filter(
        Consumption.user_id == user_id,
        Consumption.date >= start_day,
        Consumption.date <= end_day
    ).all()
    total_calories = total_protein = total_carbs = total_fat = 0
    for c in consumptions:
        total_calories += (c.food.calories_100g * c.quantity / 100)
        total_protein  += (c.food.protein_100g * c.quantity / 100)
        total_carbs    += (c.food.carbs_100g * c.quantity / 100)
        total_fat      += (c.food.fat_100g * c.quantity / 100)
    return {
        "month_start": str(start_day),
        "month_end": str(end_day),
        "user_id": user_id,
        "calories": total_calories,
        "protein": total_protein,
        "carbs": total_carbs,
        "fat": total_fat
    }

# Route pour créer un utilisateur
@app.post("/users", tags=["POST Methods"])
def create_user(user: UserCreate = Body(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    new_user = User(email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}

# Route pour créer un aliment
@app.post("/foods", tags=["POST Methods"])
def create_food(food: FoodCreate = Body(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_food = db.query(Food).filter(Food.name == food.name).first()
    if db_food:
        raise HTTPException(status_code=400, detail="Food already exists")
    new_food = Food(
        name=food.name,
        calories_100g=food.calories_100g,
        protein_100g=food.protein_100g,
        carbs_100g=food.carbs_100g,
        fat_100g=food.fat_100g
    )
    db.add(new_food)
    db.commit()
    db.refresh(new_food)
    return {"id": new_food.id, "name": new_food.name}

# Route pour créer une consommation
@app.post("/consumptions", tags=["POST Methods"])
def create_consumption(
    consumption: ConsumptionCreate = Body(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if consumption.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot create consumption for another user")
    db_user = db.query(User).filter(User.id == consumption.user_id).first()
    db_food = db.query(Food).filter(Food.id == consumption.food_id).first()
    if not db_user or not db_food:
        raise HTTPException(status_code=404, detail="User or Food not found")
    new_consumption = Consumption(
        user_id=consumption.user_id,
        food_id=consumption.food_id,
        quantity=consumption.quantity,
        date=consumption.date
    )
    db.add(new_consumption)
    db.commit()
    db.refresh(new_consumption)
    return {
        "id": new_consumption.id,
        "user_id": new_consumption.user_id,
        "food_id": new_consumption.food_id,
        "quantity": new_consumption.quantity,
        "date": str(new_consumption.date)
    }

# Route d'authentification
@app.post("/token", tags=["POST Methods"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = str(form_data.username)
    password = str(form_data.password)
    user = db.query(User).filter(User.email == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

#Route pour changer de mdp

@app.post("/change-password", tags=["POST Methods"])
def change_password(
    user_id: int,
    passwords: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot change password for another user")
    
    if not verify_password(passwords.old_password, current_user.password):
        raise HTTPException(status_code=401, detail="Old password incorrect")
    
    current_user.password = pwd_context.hash(passwords.new_password)
    db.commit()
    return {"message": "Password updated successfully"}