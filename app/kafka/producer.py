from kafka import KafkaProducer
import json
import os

producer = KafkaProducer(
    bootstrap_servers= "my-cluster-kafka-bootstrap:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)