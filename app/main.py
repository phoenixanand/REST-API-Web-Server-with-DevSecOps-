from fastapi import FastAPI, Request
from . import models
from .database import engine
from .routers import post, user, auth
from .health.v1 import health
from .config import settings
from app.logger import get_logger
from fastapi.middleware.cors import CORSMiddleware
# from app.metrics import student_validation_failure_total
from prometheus_fastapi_instrumentator import Instrumentator
import time


models.Base.metadata.create_all(bind=engine)

logger = get_logger(__name__)

app = FastAPI(
    title="Student CRUD API",
    description="A simple REST API to manage student records.",
    version="1.0.0",
)

_UNLOGGED_PATHS = {"/metrics"}

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    if request.url.path in _UNLOGGED_PATHS:
        return await call_next(request)

    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.2fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(post.router) 

app.include_router(user.router) 

app.include_router(auth.router) 

app.include_router(health.router)


@app.get("/")    
def root():
    return {"message": "hello world"}

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)