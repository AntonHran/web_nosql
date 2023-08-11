import time
import datetime

import pika

from model_ import Contact
from conn_ import con


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='email_queue', durable=True)
print(' [*cons] Waiting for messages with ObjectID from "email" contacts. To exit press Ctrl+C')


def mock_email(id_: str) -> None:
    contact: Contact = Contact.objects(id=id_).first()
    time.sleep(0.5)
    print(f"Email to e-address: {contact.email} of user with id {contact.id} was sent successfully!!!")
    contact.update(message_got=True, date_received=datetime.datetime.now())


def callback(ch, method, properties, body) -> None:
    message: str = body.decode()
    print(f' [x] Received id: {message}')
    mock_email(message)
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='email_queue', on_message_callback=callback)


if __name__ == '__main__':
    channel.start_consuming()
