from mongoengine import Document, StringField, DateTimeField, URLField
from datetime import datetime

class UserRequest(Document):
    richiesta = StringField(required=True)
    data_richiesta = DateTimeField(default=datetime.utcnow)
    url = URLField(required=False)  # URL della pagina da cui parte la richiesta
