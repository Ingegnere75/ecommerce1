from django.shortcuts import render
from .models import ContentText

def salva_contenuto(request):
    if request.method == "POST":
        titolo = request.POST.get("titolo")
        contenuto = request.POST.get("contenuto")
        url = request.POST.get("url")
        ContentText(titolo=titolo, contenuto=contenuto, url=url).save()
        return render(request, 'contentcollector/successo.html')
    return render(request, 'contentcollector/form_contenuto.html')
