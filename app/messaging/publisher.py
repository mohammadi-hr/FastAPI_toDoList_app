from fastapi import Request
from datetime import datetime
import json

def publish_message(request: Request, queue_name, message):

    channel = request.state.rabbitMQ_channel

    if not channel:
        raise RuntimeError("RabbitMQ channel not initialized!")

    channel.queue_declare(queue=queue_name, auto_delete=True)
    channel.basic_publish(exchange='',
                          routing_key='q1',
                          body=message.encode('utf-8')
                          )
    print(f"Message published in queue: {queue_name}")



def publish_log(request:Request, log_level:str, message:str, extra: dict):

    # Get the RabbitMQ channel from request.state
    channel = request.state.rabbitMQ_channel
    if not channel:
        raise RuntimeError("RabbitMQ channel not initialized!")

    queue_name = "tasks_logs"
    channel.queue_declare(queue=queue_name, auto_delete=True)

    event = {
        "timestamp": datetime.now().isoformat(),
        "log_level": log_level,
        "message": message,
        "path": str(request.url),
        "method": request.method,
        "extra": json.dumps(extra) if extra else None
    }

    body = json.dumps(event).encode('utf-8')

    channel.basic_publish(exchange='',routing_key=queue_name, body=body)

    print(f"[Log] published in queue: {queue_name} : {event}")
