from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Secret key for JWT
SECRET_KEY = "finpulse_secret_key_2024_hackathon"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User models
class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Mock user database (in production, use real database)
fake_users_db = {
    "john_doe": {
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "hashed_password": "",  # Will be set below
        "disabled": False,
        "portfolio": {
            "cash_balance": 50000.00,
            "holdings": [
                {"symbol": "AAPL", "shares": 10, "avg_price": 150.00},
                {"symbol": "GOOGL", "shares": 5, "avg_price": 2500.00},
                {"symbol": "TSLA", "shares": 8, "avg_price": 200.00}
            ]
        }
    },
    "jane_smith": {
        "username": "jane_smith",
        "email": "jane@example.com",
        "full_name": "Jane Smith",
        "hashed_password": "",  # Will be set below
        "disabled": False,
        "portfolio": {
            "cash_balance": 75000.00,
            "holdings": [
                {"symbol": "MSFT", "shares": 15, "avg_price": 300.00},
                {"symbol": "AMZN", "shares": 6, "avg_price": 3200.00},
                {"symbol": "NVDA", "shares": 12, "avg_price": 450.00}
            ]
        }
    }
}

# Set hashed passwords for demo users
fake_users_db["john_doe"]["hashed_password"] = pwd_context.hash("password123")
fake_users_db["jane_smith"]["hashed_password"] = pwd_context.hash("secure456")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt