from django.shortcuts import render
from .models import UserRequest

def salva_richiesta(request):
    if request.method == "POST":
        richiesta = request.POST.get("richiesta")
        url = request.POST.get("url")
        UserRequest(richiesta=richiesta, url=url).save()
        return render(request, 'requesttracker/successo.html')
    return render(request, 'requesttracker/form_richiesta.html')
