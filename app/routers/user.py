from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..import models, schemas, utils, oauth2
from sqlalchemy.orm import Session
from ..database import engine, get_db
from app.logger import get_logger
from app.metrics import users_created_total, database_errors_total ,duplicate_email_total

from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/users", tags=["users"])

logger = get_logger(__name__)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    hashed_pass = utils.hash(user.password)
    user.password = hashed_pass
    
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    # db.commit()
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        duplicate_email_total.inc()
        logger.warning("Duplicate email attempted: %s",user.email)
        raise HTTPException(status_code=409, detail="Duplicate email")
        
    db.refresh(new_user)
    users_created_total.inc()

    return new_user

@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {id} does not exist")
    
    
    return user 