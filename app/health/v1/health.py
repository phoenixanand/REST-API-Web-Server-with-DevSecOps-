from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/healthcheck", tags=["Health"])
def healthcheck(db: Session = Depends(get_db)):
    """Returns API status and DB connectivity status."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:  
        logger.error("Healthcheck DB connectivity failed: %s", exc)
        db_status = "unreachable"

    return {"status": "ok", "database": db_status}
