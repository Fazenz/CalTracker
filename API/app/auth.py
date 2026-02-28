from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets  # pour générer les refresh tokens

# ----------------------
# Config
# ----------------------
SECRET_KEY = "changeme_super_secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 jour
REFRESH_TOKEN_EXPIRE_DAYS = 30         # durée du refresh token

# Hachage mot de passe
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# ----------------------
# Mot de passe
# ----------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# ----------------------
# Access Token
# ----------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": int(expire.timestamp())})  # <-- converti en timestamp UNIX
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        return user_id if user_id is not None else None
    except JWTError:
        return None

# ----------------------
# Refresh Token
# ----------------------
def create_refresh_token() -> str:
    """
    Génère un refresh token aléatoire.
    """
    return secrets.token_urlsafe(32)

def is_refresh_token_valid(token_expiry: datetime) -> bool:
    """
    Vérifie si un refresh token n'est pas expiré.
    """
    return datetime.utcnow() < token_expiry