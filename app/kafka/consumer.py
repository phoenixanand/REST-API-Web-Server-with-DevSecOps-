# from kafka import KafkaConsumer
# import json
# from app.config import settings
# from app.logger import get_logger

# logger = get_logger(__name__)

# consumer = KafkaConsumer(
#     "post-events",
#     bootstrap_servers=settings.kafka_bootstrap_servers,
#     value_deserializer=lambda m: json.loads(m.decode("utf-8")),
#     group_id="notification-service",
#     auto_offset_reset="earliest",
#     enable_auto_commit=False,
# )

# for message in consumer:
#     print(message.value)


from kafka import KafkaConsumer
import json
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

def get_consumer():
    return KafkaConsumer(
        "post-events",
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        group_id="notification-service",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )

def start_consuming():
    consumer = get_consumer()
    for message in consumer:
        logger.info("Received message: %s", message.value)