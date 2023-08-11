from mongoengine import Document
from mongoengine.fields import StringField, DateField, BooleanField


class Contact(Document):
    full_name = StringField(required=True, max_length=60)
    email = StringField(required=True, max_length=50)
    message_got = BooleanField(required=True, default=False)
    date_received = DateField()
    phone = StringField(required=True, max_length=30)
    preference = StringField(choices=['email', 'SMS'])
