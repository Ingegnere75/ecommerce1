from mongoengine import Document, StringField, URLField

class ContentText(Document):
    titolo = StringField(required=True)
    contenuto = StringField()
    url = URLField(required=False)  # URL da cui viene il contenuto



# contentcollector/models.py (o se vuoi una app nuova tipo logmanager/models.py)

