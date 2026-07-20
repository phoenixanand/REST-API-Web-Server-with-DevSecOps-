
# from contextlib import contextmanager
# from time import time 

from fastapi import APIRouter

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

router = APIRouter(tags=["Metrics"])

from prometheus_client import Counter

# # Total HTTP requests
# REQUEST_COUNT = Counter(
#     "http_requests_total",
#     "Total number of HTTP requests",
#     ["method", "endpoint", "status"],
# )

# # Request latency
# REQUEST_LATENCY = Histogram(
#     "http_request_duration_seconds",
#     "HTTP request latency in seconds",
#     ["method", "endpoint"],
# )

# # Requests currently being processed
# IN_PROGRESS = Gauge(
#     "http_requests_in_progress",
#     "Number of requests currently being processed",
# )

# Post Metrics

posts_created_total = Counter("posts_created_total","Total number of posts created")

posts_updated_total = Counter("posts_updated_total","Total number of posts updated")

posts_deleted_total = Counter("posts_deleted_total","Total number of posts deleted")

# User Metrics

users_created_total = Counter("users_created_total","Total number of users created")

# Authentication Metrics

login_success_total = Counter("login_success_total","Total successful logins")

login_failure_total = Counter("login_failure_total","Total failed login attempts")

jwt_validation_failure_total = Counter("jwt_validation_failure_total", "Total JWT validation failures")

# Database Metrics

database_errors_total = Counter("database_errors_total", "Total database errors")

duplicate_email_total = Counter("duplicate_email_total", "duplicate emails")