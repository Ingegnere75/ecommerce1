from mongoengine import connect, Document, StringField

# Connessione a MongoDB Atlas
connect(
    db="ecommerce075",
    host="mongodb+srv://dmarmora0:hO6OIU41yYfrdPDO@clusterecommerce075.9hca8n3.mongodb.net/ecommerce075?retryWrites=true&w=majority&appName=ClusterEcommerce075"
)

# Modello di test
class TestDocument(Document):
    titolo = StringField(required=True)
    contenuto = StringField()

# Prova salvataggio
test_doc = TestDocument(titolo="Prova da negozio!", contenuto="Connessione MongoDB OK!")
test_doc.save()

print("✅ Documento di test salvato su MongoDB!")
