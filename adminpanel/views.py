from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json

# Modelli
from .models import LayoutSalvato
from core.models import (
    HomeCard,
    HomeBanner,
    Prodotto,
    ImmaginePersonalizzata,
    HomeElemento
)

# Decoratore solo per staff
def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

# ✅ Viste pannello admin
@login_required
def dashboard_admin(request):
    return render(request, 'adminpanel/dashboard_admin.html')

@login_required
def magazzino_admin(request):
    return render(request, 'adminpanel/magazzino_admin.html')

@login_required
def spedizioni_admin(request):
    return render(request, 'adminpanel/spedizioni_admin.html')

@login_required
def statistiche_admin(request):
    return render(request, 'adminpanel/statistiche_admin.html')

@login_required
def contatti_admin(request):
    return render(request, 'adminpanel/contatti_admin.html')

# ✅ Pagina dell’editor visuale
@staff_required
def editor_home(request):
    return render(request, 'adminpanel/editor.html')

# ✅ Importa layout della home attuale
def importa_home(request):
    html = render_to_string("core/home.html", {
        'cards': HomeCard.objects.all(),
        'homebanner': HomeBanner.objects.first(),
        'prodotti': list(Prodotto.objects.all()),
        'immagini_personalizzate': ImmaginePersonalizzata.objects.filter(attivo=True),
        'elementi_hero': HomeElemento.objects.filter(zona='hero'),
        'elementi_center': HomeElemento.objects.filter(zona='center'),
        'elementi_bottom': HomeElemento.objects.filter(zona='bottom'),
        'elementi_custom': HomeElemento.objects.filter(zona='custom'),
        'elementi_dinamici': HomeElemento.objects.all(),
        'layout_salvato': None
    })
    return HttpResponse(html)

# ✅ Salva layout in DB
@csrf_exempt
def salva_layout(request):
    if request.method == "POST":
        data = json.loads(request.body)
        contenuto = data.get("html", "")
        LayoutSalvato.objects.create(contenuto=contenuto, salvato_il=datetime.now())
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Metodo non supportato"}, status=405)

# ✅ Esporta layout attuale come JSON
def exporta_home_html(request):
    html = render_to_string("core/home.html", {})
    return JsonResponse({"html": html})
