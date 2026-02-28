from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

# --------------------------
# Modèle utilisateur
# --------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    refresh_token_expires_at = Column(DateTime, nullable=True)

    consumptions = relationship("Consumption", back_populates="user")

# --------------------------
# Modèle aliment
# --------------------------
class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    calories_100g = Column(Float, nullable=False)
    protein_100g = Column(Float, nullable=False)
    carbs_100g = Column(Float, nullable=False)
    fat_100g = Column(Float, nullable=False)

    consumptions = relationship("Consumption", back_populates="food")

# --------------------------
# Modèle consommation
# --------------------------
class Consumption(Base):
    __tablename__ = "consumptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_id = Column(Integer, ForeignKey("foods.id"))
    quantity = Column(Float, nullable=False)  # en grammes
    date = Column(Date, nullable=False)

    user = relationship("User", back_populates="consumptions")
    food = relationship("Food", back_populates="consumptions")