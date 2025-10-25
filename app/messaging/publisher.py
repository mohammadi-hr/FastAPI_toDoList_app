from fastapi import Request

def publish_message(request: Request, queue_name, message):

    request.state.queue_declare(queue=queue_name, auto_delete=True)
    request.state.basic_publish(exchange='',
                          routing_key='q1',
                          body=message.encode('utf-8')
                          )
    print(f"Message published in queue: {queue_name}")
