from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.valkey import valkey
from app.database import get_db
from app.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/healthcheck", tags=["Health"])
def healthcheck(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:  
        logger.error("Healthcheck DB connectivity failed: %s", exc)
        db_status = "unreachable"

    return {"status": "ok", "database": db_status}

@router.get("/health/live")
def liveness():
    return {"status": "ok"}  # just confirms the process is up

@router.get("/health/ready")
def readiness(response: Response, db: Session = Depends(get_db)):
    checks = {}

    try:
        valkey.ping()
        checks["valkey"] = "ok"
    except Exception as exc:
        logger.error("Readiness check failed - valkey unreachable: %s", exc)
        checks["valkey"] = "unreachable"

    all_ok = all(v == "ok" for v in checks.values())

    if not all_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ok" if all_ok else "degraded",
        "checks": checks
    }
   
