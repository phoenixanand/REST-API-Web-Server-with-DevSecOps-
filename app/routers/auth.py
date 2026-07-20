from fastapi import APIRouter, Depends, HTTPException, Response, status
from .. import database, schemas, models, utils, oauth2
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.logger import get_logger
from app.metrics import login_success_total, login_failure_total


router = APIRouter(tags=['Authentication'])
logger = get_logger(__name__)

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        login_failure_total.inc()
        logger.warning("Login failed for email=%s",user_credentials.email)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"invalid credentials")
        
    
    if not utils.verify(user_credentials.password, user.password):
        login_failure_total.inc()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid credentials")
        
    
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    login_success_total.inc()
    logger.info("Login successful for user=%s", user.email)
    
    return {"access_token": access_token, "token_type": "bearer"}
