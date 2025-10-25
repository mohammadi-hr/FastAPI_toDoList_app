
from app.messaging.connection import get_connection,get_channel

def callback(channel, method, properties, body):
    print(f"Received message: {body.decode('utf-8')}")


def start_consumer(queue_name:str):
    connection = get_connection()
    channel = get_channel()
    channel.queue_declare(queue=queue_name, auto_delete=True)
    print(f"Waiting for messages in '{queue_name}'. Press CTRL+C to exit.")
    channel.basic_comsume(queue=queue_name, on_message_callback=callback)
    try:
        channel.start_comsuming()
    except KeyboardInterrupt:
        print("Exiting consumer ...")





