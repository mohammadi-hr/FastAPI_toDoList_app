import pika
from app.core.config import settings

credentials = pika.PlainCredentials(
    username=settings.RABBITMQ_USER,
    password=settings.RABBITMQ_PASSWORD
)

def get_connection():
    return pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST,
                                                             port=settings.RABBITMQ_PORT,
                                                             credentials=credentials))

def get_channel():
    connection = get_connection()
    return connection.channel()

