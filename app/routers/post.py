from typing import List
from fastapi import Response, status, HTTPException, Depends, APIRouter
from ..import models, schemas, oauth2
from sqlalchemy.orm import Session
from app.logger import get_logger
from ..database import get_db
from typing import Optional
from app.metrics import posts_created_total, posts_updated_total, posts_deleted_total, database_errors_total
from app.valkey import valkey
import json
from app.kafka.producer import producer


router = APIRouter( prefix="/posts", tags=['post'])

logger = get_logger(__name__)

@router.get("/", response_model=List[schemas.PostResponse])    
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, search: Optional[str] = ""):

    version = valkey.get("posts:cache_version") or "1"
    cache_key = f"posts:{version}:{search}:{limit}"
    cached_posts = valkey.get(cache_key)
    if cached_posts:
        return json.loads(cached_posts)

    posts = db.query(models.Post).filter(models.Post.first_name.contains(search)).limit(limit).all()
    result = [
        schemas.PostResponse.model_validate(post).model_dump(mode="json")
        for post in posts
    ]

    valkey.setex(cache_key, 300, json.dumps(result))
    return result

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    new_post = models.Post(first_name=post.first_name, last_name=post.last_name, age=post.age, published=post.published, owner_id=current_user.id, phone_number=post.phone_number)
    db.add(new_post)
    # db.commit()
    try:
        db.commit()
    except Exception:
        db.rollback()
        database_errors_total.inc()
        logger.error("Failed to create post for user %s", current_user.id)
        raise HTTPException(status_code=500, detail="Could not create post")
       
    db.refresh(new_post)
    posts_created_total.inc()
    valkey.incr("posts:cache_version")
    logger.info("User %s created post %s",current_user.id, new_post.id)
    producer.send(
        "post-events",
        {
            "event": "post_created",
            "post_id": new_post.id,
            "first_name": new_post.first_name
        }
    )
    return new_post


@router.get("/{id}", response_model=schemas.PostResponse)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):


    cache_key = f"post:{current_user.id}:{id}"
    cached_post = valkey.get(cache_key)
    if cached_post:
        logger.info("User %s fetched post %s (cache hit)", current_user.id, id)
        return json.loads(cached_post)

    test_post = db.query(models.Post).filter(models.Post.id == id).first()
    
    if not test_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")

    if test_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized to access this post")
    
    result = schemas.PostResponse.model_validate(test_post).model_dump(mode="json")
    valkey.setex(cache_key, 300, json.dumps(result))
    logger.info("User %s fetched post %s",current_user.id, id)

    return result

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
        db.rollback()
        logger.error("Failed to delete post %s for user %s", id, current_user.id)
        database_errors_total.inc()
        raise HTTPException(status_code=500, detail="Could not delete post")

    valkey.delete(f"post:{current_user.id}:{id}")
    
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

     try:
        db.commit()
     except Exception:
        db.rollback()
        database_errors_total.inc()
        logger.error("Failed to update post %s for user %s", id, current_user.id)
        raise HTTPException(status_code=500, detail="Could not update post")
     posts_updated_total.inc()
     valkey.delete(f"post:{current_user.id}:{id}")
     logger.info("User %s updated post %s", current_user.id, id)
     return updated_posts.first()