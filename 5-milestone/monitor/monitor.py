import pika
import json
from os import getenv
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
rabbitmq_creds = pika.credentials.PlainCredentials(getenv("LOGIN_MQ"), getenv("PASSWORD_MQ"))
rabbitmq_params = pika.ConnectionParameters(getenv("URL_MQ"), 5672, getenv("VH_MQ"), rabbitmq_creds)
rabbitmq_connection = pika.BlockingConnection(rabbitmq_params)
channel = rabbitmq_connection.channel()

channel.exchange_declare('logs', 'fanout')
declared_queue = channel.queue_declare(queue='', exclusive=False)
queue = declared_queue.method.queue

channel.queue_bind(exchange="logs", queue=queue)

print('Czekam na komunikaty o błędach z well-sent. Użyj CTRL+C, aby zakończyć działanie programu.')

def callback(ch, method, properties, body):
    print(f"LOG:{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}: " + body.decode())

channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

channel.start_consuming()