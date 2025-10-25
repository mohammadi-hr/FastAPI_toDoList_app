import pika
from elasticsearch import Elasticsearch
from app.messaging.connection import get_connection,get_connection
from app.core.config import settings
import logging
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# -----------------------------
# Elasticsearch Client
# -----------------------------
es = Elasticsearch(hosts=[settings.ELASTICSEARCH_HOST])
connection = get_connection()
channel = connection.channel()


def callback(ch, method, properties, body):
    # Convert message to dict
    event = json.loads(body)

    #  Here you insert into Elasticsearch
    es.index(
        index="tasks_logs",
        document={"message": event["message"]},
    )
    print(" Message stored in Elasticsearch")

def index_to_es(event:dict):
    channel.basic_consume(queue="q1", on_message_callback=callback, auto_ack=True)
    print("🐇 Consumer started...")
    channel.start_consuming()

