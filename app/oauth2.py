from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.logger import get_logger

from app.metrics import jwt_validation_failure_total

from .config import settings

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')



SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encode = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encode 

def verify_access_token(token: str, credentials_exception): # verify the access token


    try:
       payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
       id: str = payload.get("user_id")

       if id is None:
          raise credentials_exception
    
       token_data = schemas.TokenData(id=id)

    except JWTError:
        jwt_validation_failure_total.inc()
        logger.warning("Invalid JWT token")
        raise credentials_exception
    
    
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"could not validate credentials", headers={"www-Authenticate": "bearer"})   # take the token and extract the id and token is corrct or not and automatically fetcht the users in the databse
    
    token =  verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user