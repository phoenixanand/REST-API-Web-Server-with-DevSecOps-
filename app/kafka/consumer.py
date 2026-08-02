from kafka import KafkaConsumer
import json
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

consumer = KafkaConsumer(
    "post-events",
    bootstrap_servers=settings.kafka_bootstrap_servers,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    group_id="notification-service",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
)

for message in consumer:
    print(message.value)


# for message in consumer:
#     event = message.value
#     try:
#         if event["event"] == "user_registered":
#             send_welcome_email(event["email"])  # you need to build this
#         consumer.commit()
#     except Exception:
#         logger.exception("Failed to process notification for event %s", event)
