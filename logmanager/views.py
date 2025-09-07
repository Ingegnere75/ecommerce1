from django.shortcuts import render
from .models import LogEntry

def salva_log(request):
    if request.method == "POST":
        tipo = request.POST.get("tipo")
        messaggio = request.POST.get("messaggio")
        url = request.POST.get("url")
        LogEntry(tipo=tipo, messaggio=messaggio, url=url).save()
        return render(request, 'logmanager/successo.html')
    return render(request, 'logmanager/form_log.html')
