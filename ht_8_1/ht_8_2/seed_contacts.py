import datetime
from random import randint, choice

from faker import Faker

from model_ import Contact
from conn_ import con


fake = Faker()
number_contacts: int = 50


def seed_contacts() -> list[Contact]:
    contacts: list[Contact] = []
    for _ in range(randint(1, number_contacts)):
        contact = Contact(
            full_name=fake.first_name() + ' ' + fake.last_name(),
            email=fake.ascii_free_email(),
            message_got=False,
            date_received=datetime.date(year=1990, month=1, day=1),
            phone=fake.phone_number(),
            preference=choice(['email', 'SMS'])
        ).save()
        contacts.append(contact)
    return contacts
