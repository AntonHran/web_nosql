import datetime

from mongoengine import Document, CASCADE, ValidationError
from mongoengine.fields import StringField, DateField, ListField, ReferenceField


class Author(Document):
    full_name = StringField(required=True, max_length=60)
    born_date = DateField(required=True)
    born_location = StringField(required=True, max_length=100)
    description = StringField(max_length=4000)

    def validate_born_date(self, value: datetime):
        if value >= datetime.date.today():
            raise ValidationError("Birth date must be in the past!")
        else:
            self.born_date = value


class Quote(Document):
    tags = ListField(StringField(required=False), required=False)
    author = ReferenceField(Author, reverse_delete_rule=CASCADE)
    quote = StringField(required=True)
    meta = {"allow_inheritance": True}
