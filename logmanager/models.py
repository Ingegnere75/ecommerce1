from mongoengine import Document, StringField, DateTimeField, URLField
from datetime import datetime

class LogEntry(Document):
    tipo = StringField(required=True)  # es: "ERROR", "INFO", "WARNING", "USER_ACTION"
    messaggio = StringField()
    data_log = DateTimeField(default=datetime.utcnow)
    url = URLField(required=False)  # URL dove si è verificato il log
