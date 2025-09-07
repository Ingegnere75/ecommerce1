# contentcollector/utils.py

from contentcollector.models import ContentText

def salva_contenuto(titolo, contenuto, url):
    # Cerca se esiste già un contenuto con lo stesso titolo
    esistente = ContentText.objects(titolo=titolo).first()

    if esistente:
        # Se esiste, aggiorna il contenuto e l'url
        esistente.contenuto = contenuto
        esistente.url = url
        esistente.save()
    else:
        # Se non esiste, crea un nuovo documento
        ContentText(titolo=titolo, contenuto=contenuto, url=url).save()
