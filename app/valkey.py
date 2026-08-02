from .config import settings
from redis import Redis

VALKEY_HOST=settings.valkey_host
VALKEY_PORT=settings.valkey_port

valkey = Redis(
    host=("VALKEY_HOST"),
    port=int((VALKEY_PORT)),
    decode_responses=True,
)