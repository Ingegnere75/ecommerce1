from mongoengine import Document, StringField, DateTimeField, DictField
from datetime import datetime

class LogEvento(Document):
    sezione = StringField(required=True)
    azione = StringField(required=True)
    dettagli = DictField()
    utente_email = StringField(required=False)
    utente_username = StringField(required=False)
    session_key = StringField(required=False)
    timestamp = DateTimeField(default=datetime.now)
