from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import asyncio
import yfinance as yf

# Import auth functions
from jose import JWTError, jwt
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# Secret key for JWT
SECRET_KEY = "finpulse_secret_key_2024_hackathon"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(
    title="FinPulse API",
    description="AI Investment Intelligence Platform",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class Portfolio(BaseModel):
    cash_balance: float
    holdings: List[dict]

class Trade(BaseModel):
    symbol: str
    shares: int
    action: str  # "buy" or "sell"

# Dynamic Engine (No API keys needed, No pandas-ta dependency)
class DynamicFinPulseEngine:
    """Real-time Dynamic Engine using yfinance (NO API KEYS)"""
    
    def __init__(self):
        self.popular_stocks = [
            "AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", 
            "META", "NFLX", "AMD", "INTC", "SPY", "QQQ"
        ]
    
    async def get_real_stock_data(self, symbol: str):
        """Get REAL stock data with technical indicators"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="2mo", interval="1d")
            info = stock.info
            
            if hist.empty or len(hist) < 10:
                return await self._get_smart_fallback(symbol)
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            price_change = current_price - prev_price
            price_change_percent = (price_change / prev_price) * 100
            
            # Calculate technical indicators manually (no pandas-ta)
            rsi = self._calculate_rsi_manual(hist['Close'])
            macd, macd_signal = self._calculate_macd_manual(hist['Close'])
            sma_20 = self._calculate_sma_manual(hist['Close'], 20)
            sma_50 = self._calculate_sma_manual(hist['Close'], 50)
            volume_avg = hist['Volume'].tail(20).mean()
            
            return {
                "symbol": symbol.upper(),
                "current_price": round(current_price, 2),
                "price_change": round(price_change, 2),
                "price_change_percent": round(price_change_percent, 2),
                "company_name": info.get('longName', symbol),
                "volume": hist['Volume'].iloc[-1],
                "volume_avg": volume_avg,
                "market_cap": info.get('marketCap', 0),
                "rsi": round(rsi, 2),
                "macd": round(macd, 4),
                "macd_signal": round(macd_signal, 4),
                "sma_20": round(sma_20, 2),
                "sma_50": round(sma_50, 2),
                "is_real_data": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching real data for {symbol}: {e}")
            return await self._get_smart_fallback(symbol)
    
    async def calculate_dynamic_pulsescore(self, symbol: str):
        """Calculate INTELLIGENT PulseScore using real technical analysis"""
        try:
            stock_data = await self.get_real_stock_data(symbol)
            
            if not stock_data.get('is_real_data', False):
                return self._create_smart_pulsescore(symbol, stock_data)
            
            price_change = stock_data['price_change_percent']
            rsi = stock_data['rsi']
            macd = stock_data['macd']
            volume_ratio = stock_data['volume'] / stock_data['volume_avg']
            
            # Calculate component scores
            momentum_score = self._calculate_momentum_score(price_change, macd)
            trend_score = self._calculate_trend_score(stock_data)
            volume_score = self._calculate_volume_score(volume_ratio)
            rsi_score = self._calculate_rsi_score(rsi)
            
            # Weighted composite score
            pulsescore = (
                momentum_score * 0.35 +
                trend_score * 0.30 +
                volume_score * 0.20 +
                rsi_score * 0.15
            )
            
            # Determine trend and recommendation
            trend, recommendation, color = self._determine_trend_recommendation(
                pulsescore, price_change, rsi, macd
            )
            
            return {
                "symbol": symbol.upper(),
                "pulsescore": max(0, min(100, round(pulsescore, 1))),
                "trend": trend,
                "recommendation": recommendation,
                "color": color,
                "current_price": stock_data['current_price'],
                "price_change_percent": stock_data['price_change_percent'],
                "confidence": self._calculate_confidence(pulsescore, volume_ratio),
                "breakdown": {
                    "momentum": round(momentum_score, 1),
                    "trend": round(trend_score, 1),
                    "volume": round(volume_score, 1),
                    "rsi": round(rsi_score, 1)
                },
                "technical_indicators": {
                    "rsi": rsi,
                    "macd": macd,
                    "price_vs_sma20": round(((stock_data['current_price'] / stock_data['sma_20']) - 1) * 100, 2),
                    "volume_ratio": round(volume_ratio, 2)
                },
                "is_real_data": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in dynamic pulsescore for {symbol}: {e}")
            return self._create_smart_pulsescore(symbol)
    
    async def calculate_dynamic_risk_analysis(self, symbol: str):
        """Calculate REAL risk analysis using volatility"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="3mo")
            
            if hist.empty or len(hist) < 20:
                return self._create_smart_risk(symbol)
            
            # Calculate REAL volatility
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            
            # Calculate max drawdown
            rolling_max = hist['Close'].expanding().max()
            daily_drawdown = hist['Close'] / rolling_max - 1
            max_drawdown = daily_drawdown.min()
            
            # Risk scoring
            risk_score = self._calculate_comprehensive_risk_score(volatility, max_drawdown)
            risk_level, color = self._determine_risk_level(risk_score)
            
            return {
                "symbol": symbol.upper(),
                "risk_level": risk_level,
                "risk_score": min(100, max(0, risk_score)),
                "color": color,
                "volatility": round(volatility, 3),
                "max_drawdown": round(abs(max_drawdown * 100), 1),
                "sharpe_ratio": round((returns.mean() / returns.std()) * np.sqrt(252), 2) if returns.std() > 0 else 0,
                "stress_test": self._calculate_stress_scenarios(volatility, max_drawdown),
                "is_real_data": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in dynamic risk analysis for {symbol}: {e}")
            return self._create_smart_risk(symbol)
    
    async def get_dynamic_opportunities(self):
        """Find REAL market opportunities"""
        opportunities = []
        
        for symbol in self.popular_stocks[:6]:
            try:
                stock_data = await self.get_real_stock_data(symbol)
                
                if not stock_data.get('is_real_data', False):
                    continue
                
                price_change = stock_data['price_change_percent']
                volume_ratio = stock_data['volume'] / stock_data['volume_avg']
                rsi = stock_data['rsi']
                macd = stock_data['macd']
                
                opportunity_score = 0
                opportunity_type = ""
                reasoning = []
                
                # Momentum Opportunity
                if price_change > 3 and volume_ratio > 1.5 and macd > 0:
                    opportunity_score = 85
                    opportunity_type = "Momentum Breakout"
                    reasoning.append("Strong price momentum with high volume")
                
                # Oversold Bounce
                elif price_change < -5 and rsi < 30 and volume_ratio > 1.2:
                    opportunity_score = 80
                    opportunity_type = "Oversold Bounce"
                    reasoning.append("Oversold conditions with potential reversal")
                
                # Volume Spike
                elif volume_ratio > 2.0 and abs(price_change) > 1:
                    opportunity_score = 75
                    opportunity_type = "Volume Spike"
                    reasoning.append("Unusual volume activity detected")
                
                if opportunity_score > 70:
                    opportunities.append({
                        "symbol": symbol,
                        "name": stock_data['company_name'],
                        "type": opportunity_type,
                        "confidence": min(95, opportunity_score - 10),
                        "potential_return": round(abs(price_change) * 1.5 + 5, 1),
                        "current_change": round(price_change, 2),
                        "current_price": stock_data['current_price'],
                        "reasoning": reasoning,
                        "opportunity_score": opportunity_score,
                        "is_real_data": True,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                print(f"Error analyzing opportunity for {symbol}: {e}")
                continue
        
        return sorted(opportunities, key=lambda x: x['opportunity_score'], reverse=True)[:4]
    
    async def get_market_overview(self):
        """Get REAL market overview"""
        try:
            # Get SPY for market sentiment
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period="1mo")
            
            if not spy_hist.empty:
                spy_change = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0] - 1) * 100
                market_sentiment = "Bullish" if spy_change > 1 else "Bearish" if spy_change < -1 else "Neutral"
            else:
                spy_change = 0
                market_sentiment = "Neutral"
            
            return {
                "market_sentiment": market_sentiment,
                "spy_performance": round(spy_change, 2),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in market overview: {e}")
            return {
                "market_sentiment": "Neutral",
                "spy_performance": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    # Manual Technical Analysis Methods (No pandas-ta)
    def _calculate_rsi_manual(self, prices, period=14):
        """Calculate RSI manually"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1] if not rsi.empty else 50
        except:
            return 50
    
    def _calculate_macd_manual(self, prices):
        """Calculate MACD manually"""
        try:
            exp1 = prices.ewm(span=12).mean()
            exp2 = prices.ewm(span=26).mean()
            macd = exp1 - exp2
            macd_signal = macd.ewm(span=9).mean()
            return macd.iloc[-1] if not macd.empty else 0, macd_signal.iloc[-1] if not macd_signal.empty else 0
        except:
            return 0, 0
    
    def _calculate_sma_manual(self, prices, period):
        """Calculate Simple Moving Average manually"""
        try:
            return prices.rolling(window=period).mean().iloc[-1]
        except:
            return prices.iloc[-1] if not prices.empty else 0
    
    def _calculate_momentum_score(self, price_change, macd):
        momentum = 50
        momentum += min(25, abs(price_change) * 2) * (1 if price_change > 0 else -1)
        momentum += macd * 1000
        return max(0, min(100, momentum))
    
    def _calculate_trend_score(self, stock_data):
        score = 50
        if stock_data['current_price'] > stock_data['sma_20']:
            score += 20
        if stock_data['current_price'] > stock_data['sma_50']:
            score += 20
        if stock_data['sma_20'] > stock_data['sma_50']:
            score += 10
        return min(100, score)
    
    def _calculate_volume_score(self, volume_ratio):
        if volume_ratio > 2.0: return 90
        elif volume_ratio > 1.5: return 75
        elif volume_ratio > 1.0: return 60
        elif volume_ratio > 0.7: return 50
        else: return 30
    
    def _calculate_rsi_score(self, rsi):
        if 40 <= rsi <= 60: return 80
        elif 30 <= rsi <= 70: return 60
        elif rsi > 70 or rsi < 30: return 30
        else: return 50
    
    def _determine_trend_recommendation(self, pulsescore, price_change, rsi, macd):
        if pulsescore >= 80 and price_change > 2 and macd > 0:
            return "Strong Bullish", "Strong Buy", "text-green-600"
        elif pulsescore >= 65 and price_change > 0:
            return "Bullish", "Buy", "text-green-500"
        elif pulsescore >= 40:
            return "Neutral", "Hold", "text-yellow-500"
        elif pulsescore >= 20:
            return "Bearish", "Sell", "text-orange-500"
        else:
            return "Strong Bearish", "Strong Sell", "text-red-600"
    
    def _calculate_confidence(self, pulsescore, volume_ratio):
        base_confidence = min(95, pulsescore * 0.8)
        volume_boost = min(15, (volume_ratio - 1) * 10) if volume_ratio > 1 else 0
        return round(base_confidence + volume_boost, 1)
    
    def _calculate_comprehensive_risk_score(self, volatility, max_drawdown):
        return min(100, volatility * 25 + abs(max_drawdown) * 30)
    
    def _determine_risk_level(self, risk_score):
        if risk_score < 30: return "Low", "green"
        elif risk_score < 60: return "Medium", "orange"
        else: return "High", "red"
    
    def _calculate_stress_scenarios(self, volatility, max_drawdown):
        return {
            "market_crash": round(-(volatility * 100 + 10), 1),
            "recession": round(-(volatility * 80 + 8), 1),
            "volatility_spike": round(-(volatility * 60 + 5), 1)
        }
    
    async def _get_smart_fallback(self, symbol):
        symbol_hash = hash(symbol) % 100
        return {
            "symbol": symbol.upper(),
            "current_price": round(50 + symbol_hash, 2),
            "price_change": round((symbol_hash - 50) / 10, 2),
            "price_change_percent": round((symbol_hash - 50) / 2, 2),
            "company_name": f"{symbol} Corporation",
            "volume": 1000000 + symbol_hash * 10000,
            "volume_avg": 1500000,
            "rsi": 40 + symbol_hash % 30,
            "macd": (symbol_hash - 50) / 1000,
            "macd_signal": (symbol_hash - 50) / 1500,
            "sma_20": round(55 + symbol_hash, 2),
            "sma_50": round(52 + symbol_hash, 2),
            "is_real_data": False,
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_smart_pulsescore(self, symbol, stock_data=None):
        symbol_hash = hash(symbol) % 100
        pulsescore = 30 + symbol_hash % 60
        
        if pulsescore >= 70:
            trend, recommendation, color = "Bullish", "Buy", "text-green-500"
        elif pulsescore >= 40:
            trend, recommendation, color = "Neutral", "Hold", "text-yellow-500"
        else:
            trend, recommendation, color = "Bearish", "Sell", "text-orange-500"
        
        return {
            "symbol": symbol.upper(),
            "pulsescore": pulsescore,
            "trend": trend,
            "recommendation": recommendation,
            "color": color,
            "confidence": min(90, pulsescore + 20),
            "is_real_data": False,
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_smart_risk(self, symbol):
        symbol_hash = hash(symbol) % 100
        if symbol_hash < 30:
            risk_level, color, risk_score = "Low", "green", 20 + symbol_hash
        elif symbol_hash < 70:
            risk_level, color, risk_score = "Medium", "orange", 40 + symbol_hash
        else:
            risk_level, color, risk_score = "High", "red", 60 + symbol_hash
        
        return {
            "symbol": symbol.upper(),
            "risk_level": risk_level,
            "risk_score": risk_score,
            "color": color,
            "volatility": round(0.1 + symbol_hash / 200, 3),
            "max_drawdown": round(5 + symbol_hash / 4, 1),
            "beta": round(0.5 + symbol_hash / 100, 2),
            "is_real_data": False,
            "timestamp": datetime.now().isoformat()
        }

# Initialize dynamic engine
engine = DynamicFinPulseEngine()

# Helper function to safely hash passwords
def safe_hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Mock user database
fake_users_db = {
    "john_doe": {
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "hashed_password": "",
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
        "hashed_password": "",
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

# Startup event to initialize passwords
@app.on_event("startup")
async def startup_event():
    fake_users_db["john_doe"]["hashed_password"] = safe_hash_password("password123")
    fake_users_db["jane_smith"]["hashed_password"] = safe_hash_password("secure456")

# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return safe_hash_password(password)

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

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
async def register_user(user_data: UserCreate):
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    fake_users_db[user_data.username] = {
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "disabled": False,
        "portfolio": {
            "cash_balance": 100000.00,
            "holdings": []
        }
    }
    
    return {"message": "User created successfully", "username": user_data.username}

# Protected routes
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/me/portfolio")
async def get_user_portfolio(current_user: User = Depends(get_current_active_user)):
    user_data = fake_users_db[current_user.username]
    return user_data["portfolio"]

# DYNAMIC FinPulse endpoints
@app.get("/api/pulsescore/{symbol}")
async def get_pulsescore(symbol: str):
    """Get DYNAMIC PulseScore analysis with real data"""
    return await engine.calculate_dynamic_pulsescore(symbol)

@app.get("/api/risk/{symbol}")
async def get_risk_radar(symbol: str):
    """Get DYNAMIC risk analysis with real volatility"""
    return await engine.calculate_dynamic_risk_analysis(symbol)

@app.get("/api/hedge/{symbol}")
async def get_hedge_suggestions(symbol: str, current_user: User = Depends(get_current_active_user)):
    """Get hedge suggestions for a stock"""
    await asyncio.sleep(0.4)
    user_data = fake_users_db[current_user.username]
    
    # Mock hedge suggestions (can be enhanced)
    hedge_options = [
        {
            "type": "Inverse ETF",
            "symbol": "SQQQ" if symbol in ["AAPL", "MSFT", "GOOGL"] else "SPXU",
            "description": "Inverse ETF to hedge against tech downturn",
            "effectiveness": random.randint(75, 90),
            "cost": "Low"
        },
        {
            "type": "Options Strategy",
            "symbol": f"{symbol} Put Options",
            "description": "Protective puts to limit downside",
            "effectiveness": random.randint(80, 95),
            "cost": "Medium"
        }
    ]
    
    return {
        "symbol": symbol.upper(),
        "hedge_score": random.randint(65, 90),
        "suggestions": hedge_options,
        "portfolio_impact": f"Reduces portfolio risk by {random.randint(15, 40)}%",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/opportunities")
async def get_opportunities():
    """Get REAL market opportunities"""
    return {
        "timestamp": datetime.now().isoformat(),
        "opportunities": await engine.get_dynamic_opportunities()
    }

@app.get("/api/market/overview")
async def get_market_overview():
    """Get REAL market overview"""
    return await engine.get_market_overview()

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str):
    """Get REAL stock data"""
    return await engine.get_real_stock_data(symbol)

@app.post("/api/trade")
async def execute_trade(trade: Trade, current_user: User = Depends(get_current_active_user)):
    """Execute a trade"""
    user_data = fake_users_db[current_user.username]
    portfolio = user_data["portfolio"]
    
    # Get real current price
    stock_data = await engine.get_real_stock_data(trade.symbol)
    current_price = stock_data.get('current_price', 100)
    
    total_cost = current_price * trade.shares
    
    if trade.action == "buy":
        if portfolio["cash_balance"] < total_cost:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        portfolio["cash_balance"] -= total_cost
        
        existing_holding = next((h for h in portfolio["holdings"] if h["symbol"] == trade.symbol), None)
        if existing_holding:
            existing_holding["shares"] += trade.shares
            existing_holding["avg_price"] = (
                (existing_holding["avg_price"] * existing_holding["shares"] + total_cost) / 
                (existing_holding["shares"] + trade.shares)
            )
        else:
            portfolio["holdings"].append({
                "symbol": trade.symbol.upper(),
                "shares": trade.shares,
                "avg_price": current_price
            })
    
    elif trade.action == "sell":
        existing_holding = next((h for h in portfolio["holdings"] if h["symbol"] == trade.symbol), None)
        if not existing_holding or existing_holding["shares"] < trade.shares:
            raise HTTPException(status_code=400, detail="Insufficient shares")
        
        portfolio["cash_balance"] += total_cost
        existing_holding["shares"] -= trade.shares
        
        if existing_holding["shares"] == 0:
            portfolio["holdings"].remove(existing_holding)
    
    return {
        "message": f"Successfully {trade.action} {trade.shares} shares of {trade.symbol}",
        "current_cash": portfolio["cash_balance"],
        "trade_value": total_cost
    }

@app.get("/api/portfolio/analysis")
async def analyze_portfolio(current_user: User = Depends(get_current_active_user)):
    """Analyze user portfolio with REAL current prices"""
    user_data = fake_users_db[current_user.username]
    portfolio = user_data["portfolio"]
    
    total_invested = 0
    total_current = portfolio["cash_balance"]
    holdings_value = 0
    
    for holding in portfolio["holdings"]:
        symbol = holding["symbol"]
        
        # Get REAL current price
        stock_data = await engine.get_real_stock_data(symbol)
        current_price = stock_data.get('current_price', holding["avg_price"] * 1.1)
        
        invested = holding["shares"] * holding["avg_price"]
        current_value = holding["shares"] * current_price
        
        total_invested += invested
        total_current += current_value
        holdings_value += current_value
        
        holding["current_price"] = round(current_price, 2)
        holding["current_value"] = round(current_value, 2)
        holding["gain_loss"] = round(current_value - invested, 2)
        holding["gain_loss_percent"] = round(((current_value - invested) / invested) * 100, 2) if invested > 0 else 0
    
    total_gain_loss = total_current - total_invested
    total_gain_loss_percent = (total_gain_loss / total_invested) * 100 if total_invested > 0 else 0
    
    insights = []
    if len(portfolio["holdings"]) < 3:
        insights.append("Consider diversifying your portfolio with more holdings")
    if portfolio["cash_balance"] / total_current > 0.3:
        insights.append("High cash position - consider deploying into opportunities")
    if any(h["gain_loss_percent"] < -10 for h in portfolio["holdings"]):
        insights.append("Some positions are down significantly - review risk management")
    if not insights:
        insights.append("Portfolio is well-balanced. Consider exploring new opportunities")
    
    return {
        "total_invested": round(total_invested, 2),
        "total_current_value": round(total_current, 2),
        "cash_balance": round(portfolio["cash_balance"], 2),
        "holdings_value": round(holdings_value, 2),
        "total_gain_loss": round(total_gain_loss, 2),
        "total_gain_loss_percent": round(total_gain_loss_percent, 2),
        "holdings": portfolio["holdings"],
        "ai_insights": insights,
        "overall_risk": random.choice(["Low", "Medium", "High"]),
        "diversification_score": random.randint(60, 95),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    return {
        "message": "🚀 FinPulse Dynamic API is running!",
        "version": "3.0.0",
        "features": "Real-time market data, Technical analysis, Dynamic scoring",
        "demo_accounts": {
            "john_doe": "password123",
            "jane_smith": "secure456"
        },
        "endpoints": {
            "auth": "/token, /register",
            "analysis": "/api/pulsescore/{symbol}, /api/risk/{symbol}, /api/hedge/{symbol}",
            "market_data": "/api/stock/{symbol}, /api/market/overview",
            "trading": "/api/trade",
            "opportunities": "/api/opportunities",
            "portfolio": "/api/portfolio/analysis",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")