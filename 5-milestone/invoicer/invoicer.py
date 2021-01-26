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

channel.exchange_declare('invoices', 'fanout')
declared_queue = channel.queue_declare(queue='', exclusive=False)
queue = declared_queue.method.queue

channel.queue_bind(exchange="invoices", queue=queue)

print('Czekam na otrzymanie powiadomień o odebraniu paczki. Użyj CTRL+C, aby zakończyć działanie programu.')

def callback(ch, method, properties, body):
    try:
        body = json.loads(body)
        print(body)
        package_id = body['id']
        print(package_id)
        sender = body['sender']
        timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        print(timestamp)
        f = open(f'invoice_{package_id}_{timestamp}.txt', 'w', encoding='utf-8')
        f.write(f'Faktura do paczki {package_id}\n')
        f.write(f'Dla Pan/i {sender}\n')
        f.write(f'{timestamp}\n')
        f.write(f'Do zapłacenia pińcet pieniążków')
        f.close()
        print("Wygenerowano fakturę dla paczki %r" % body["id"])
    except:
        print('Wystąpił błąd przy przetwarzaniu wiadomości:')
        print(body)

channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

channel.start_consuming()