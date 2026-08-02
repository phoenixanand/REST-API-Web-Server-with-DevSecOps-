from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "post-events",
    bootstrap_servers="...",
    value_deserializer=...,
    group_id="post-events-processor",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
)

for message in consumer:
    print(message.value)