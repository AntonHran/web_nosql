import pika

from model_ import Contact
from seed_contacts import seed_contacts


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)
)
channel = connection.channel()

channel.exchange_declare(exchange='message_exchange', exchange_type='direct')
channel.queue_declare(queue='email_queue', durable=True)
channel.queue_declare(queue='sms_queue', durable=True)
channel.queue_bind(exchange='message_exchange', queue='email_queue')
channel.queue_bind(exchange='message_exchange', queue='sms_queue')


def queue_through(exchange: str, key: str, obj: Contact) -> None:
    channel.basic_publish(
        exchange=exchange,
        routing_key=key,
        body=str(obj.id).encode(),
        properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
    )
    print(f" [x prod] %r was sent through {key}" % obj.id)


def prod_work() -> None:
    created_contacts: list[Contact] = seed_contacts()
    for contact in created_contacts:
        if contact.preference == 'email':
            queue_through(exchange='message_exchange', key='email_queue', obj=contact)
        elif contact.preference == 'SMS':
            queue_through(exchange="message_exchange", key="sms_queue", obj=contact)
    connection.close()


if __name__ == '__main__':
    prod_work()
