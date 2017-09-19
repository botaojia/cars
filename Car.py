from mongoengine import Document, StringField, IntField, FloatField

class Car(Document):
    zipcode = StringField(length=5)
    brand = StringField(max_length=15)
    model = StringField()
    price = IntField()
    miles = IntField()
    year = IntField()
    exterior = StringField()
    meta = { 'indexes': [('zipcode', 'brand', 'model')] }
    
class carStat(Document):
    zipcode = StringField(length=5)
    brand = StringField(max_length=15)
    model = StringField()
    number = IntField()
    meta = { 'indexes': [('zipcode')] }