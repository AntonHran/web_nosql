import time
import datetime

import pika

from model_ import Contact
from conn_ import con


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='sms_queue', durable=True)
print(' [*cons] Waiting for messages with ObjectID from "sms" contacts. To exit press Ctrl+C')


def mock_sms(id_: str) -> None:
    contact: Contact = Contact.objects(id=id_).first()
    time.sleep(0.5)
    print(f"SMS to phone number: {contact.phone} of user with id {contact.id} was sent successfully!!!")
    contact.update(message_got=True, date_received=datetime.date.today())


def callback(ch, method, properties, body) -> None:
    message: str = body.decode()
    print(f' [x] Received id: {message}')
    mock_sms(message)
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='sms_queue', on_message_callback=callback)


if __name__ == '__main__':
    channel.start_consuming()
