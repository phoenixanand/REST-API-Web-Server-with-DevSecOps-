# from kafka import KafkaProducer
# import json
# from app.config import settings


# producer = KafkaProducer(
#     bootstrap_servers= settings.kafka_bootstrap_servers,
#     value_serializer=lambda v: json.dumps(v).encode("utf-8")
# )

from kafka import KafkaProducer
import json
from app.config import settings

_producer = None

def get_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
    return _producer

class _LazyProducer:
    def send(self, *args, **kwargs):
        return get_producer().send(*args, **kwargs)

producer = _LazyProducer()