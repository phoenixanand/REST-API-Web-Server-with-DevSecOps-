from typing import List
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..import models, schemas, utils, oauth2
from sqlalchemy.orm import Session
from app.logger import get_logger
from ..database import engine, get_db
from typing import Optional
from app.metrics import posts_created_total, posts_updated_total, posts_deleted_total, database_errors_total

router = APIRouter( prefix="/posts", tags=['post'])

logger = get_logger(__name__)

@router.get("/", response_model=List[schemas.PostResponse])    
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, search: Optional[str] = ""):

    posts = db.query(models.Post).filter(models.Post.first_name.contains(search)).limit(limit).all()
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    new_post = models.Post(first_name=post.first_name, last_name=post.last_name, age=post.age, published=post.published, owner_id=current_user.id, phone_number=post.phone_number)
    db.add(new_post)
    # db.commit()
    try:
        db.commit()
    except Exception:
        database_errors_total.inc()
    db.refresh(new_post)
    posts_created_total.inc()
    logger.info("User %s created post %s",current_user.id, new_post.id)
    return new_post


@router.get("/{id}", response_model=List[schemas.PostResponse])
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
   
    test_post = db.query(models.Post).filter(models.Post.id == id).all()
    
    if not test_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")
    
    logger.info("User %s fetched post %s",current_user.id, id)

    return test_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    testa_post = db.query(models.Post).filter(models.Post.id == id)
    
    post = testa_post.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    
    if post.owner_id != current_user.id:
        logger.warning("User %s tried to delete post %s owned by user %s",current_user.id,id,post.owner_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized to perform requested action")
    testa_post.delete(synchronize_session=False)
    # db.commit()
    try:
        db.commit()
    except Exception:
        database_errors_total.inc()
    
    logger.info("User %s deleted post %s",current_user.id,id)
    posts_deleted_total.inc()
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

     updated_posts = db.query(models.Post).filter(models.Post.id == id)
     updaa = updated_posts.first()
     if updaa == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
     if updaa.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized to perform requested action")
     updated_posts.update(post.dict(), synchronize_session=False)
     db.commit()
     posts_updated_total.inc()

     return updated_posts.first()