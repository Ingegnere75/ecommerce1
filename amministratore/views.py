from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMessage
from django import forms
from django.template.loader import get_template
from django.utils.timezone import now, timedelta
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.db.models.functions import TruncDate
from decimal import Decimal
from pymongo import MongoClient
from negozio import settings
from xhtml2pdf import pisa
from .models  import Contenuto,Richiesta
# Modelli
from core.models import (
    Prodotto, Categoria, SottoCategoria, Ordine,
    OrdineItem, MessaggioContatto, PaginaInformativa,
    ContattiBrand, Brand, HomeCard, HomeBanner,
    HomeElemento, PrezzoSpedizione, CodiceSconto,
    CookieConsent, InteractionLog, StrisciaInfo
)
from accounts.models import UserProfile, Reclamo, STATO_CHOICES, ESITO_CHOICES
from amministratore.models import EntrataMagazzino, Contenuto, Richiesta, PaymentSettings, SiteSettings
from blog.models import ArticoloBlog, CommentoBlog, ProdottoSuggerito, BannerInformativo

# Form
from .forms import (
    ProdottoForm, EntrataMagazzinoForm, ContattiBrandForm,
    CategoriaForm,  BrandForm,
    HomeCardForm, HomeBannerForm, HomeElementoForm,
    PrezzoSpedizioneForm, CodiceScontoGeneraForm,
    StrisciaInfoForm, ArticoloBlogForm, BannerInformativoForm,
    ProdottoSuggeritoForm
)
from accounts.forms import ModificaProfiloForm
from datetime import datetime
# Altri
from core.widgets import ColoriPreviewWidget
from core.colori import COLORI_NOMI
from core.services.logger_mongo import LogEvento
from collections import defaultdict
from .forms import ContenutoForm, RichiestaForm
from datetime import timezone
from django.utils import timezone
from amministratore.forms import SottoCategoriaForm



#---------------------------------------------------------------------------------------------------------
#                 Varie
#----------------------------------------------------------------------------------------------------------


def is_admin(user):
    return user.is_authenticated and user.is_staff

#--------------------------------------------------------------------------------------------------------
@user_passes_test(is_admin)
def dashboard(request):
    return render(request, 'amministratore/dashboard.html')
#----------------------------------------------------------------------------------------------------------
def dashboard(request):
    settings = SiteSettings.objects.first()
    maintenance_mode = settings.maintenance_mode if settings else False
    return render(request, 'amministratore/dashboard.html', {'maintenance_mode': maintenance_mode})

#-------------------------------------------------------------------------------------------------------------
#    categorie
#-----------------------------------------------------------------------------------------------------------------
def categorie_admin_view(request):
    categorie = Categoria.objects.all()
    return render(request, 'amministratore/categorie.html', {'categorie': categorie})

#-------------------------------------------------------------------------------------------------------------------


def categorie_list(request):
    categorie = Categoria.objects.all()
    return render(request, 'amministratore/categorie.html', {'categorie': categorie})
#--------------------------------------------------------------------------------------------------------------
def aggiungi_categoria(request):
    form = CategoriaForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Categoria aggiunta con successo!")
        return redirect('categorie_list')
    return render(request, 'amministratore/categoria_form.html', {'form': form, 'titolo': "Aggiungi Categoria"})

#----------------------------------------------------------------------------------------------------------------
def modifica_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    form = CategoriaForm(request.POST or None, request.FILES or None, instance=categoria)
    if form.is_valid():
        form.save()
        messages.success(request, "Categoria modificata!")
        return redirect('categorie_list')
    return render(request, 'amministratore/categoria_form.html', {'form': form, 'titolo': "Modifica Categoria"})
#-----------------------------------------------------------------------------------------------------------------
def elimina_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    categoria.delete()
    messages.warning(request, "Categoria eliminata!")
    return redirect('categorie_list')
#-------------------------------------------------------------------------------------------------------------------------
#    sottocategorie
#------------------------------------------------------------------------------------------------------------------------------------

def sottocategorie_admin_view(request):
    sottocategorie = SottoCategoria.objects.select_related('categoria').all()
    return render(request, 'amministratore/sottocategorie.html', {'sottocategorie': sottocategorie})

#------------------------------------------------------------------------------------------------------------------------------

def sottocategorie_admin_view(request):
    sottocategorie = SottoCategoria.objects.select_related('categoria').all()
    return render(request, 'amministratore/sottocategorie.html', {'sottocategorie': sottocategorie})
#-----------------------------------------------------------------------------------------------------------------------------


def aggiungi_sottocategoria(request):
    print("📥 Metodo:", request.method)

    if request.method == 'POST':
        print("✅ POST ricevuto!")
        form = SottoCategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            print("✅ Form salvato con successo!")
            return redirect('admin-sottocategoria')
        else:
            print("❌ Form non valido:")
            print(form.errors)
    else:
        print("🟡 GET - form iniziale")
        form = SottoCategoriaForm()

    return render(request, 'amministratore/sottocategoria_form.html', {
        'form': form,
        'titolo': '➕ Aggiungi Sottocategoria'
    })


#--------------------------------------------------------------------------------------------------------------
# Modifica sottocategoria
def modifica_sottocategoria(request, id):
    sottocategoria = get_object_or_404(SottoCategoria, id=id)
    if request.method == 'POST':
        form = SottoCategoriaForm(request.POST, request.FILES, instance=sottocategoria)
        if form.is_valid():
            form.save()
            return redirect('admin-sottocategoria')
    else:
        form = SottoCategoriaForm(instance=sottocategoria)

    return render(request, 'amministratore/sottocategoria_form.html', {
        'form': form,
        'titolo': '✏️ Modifica Sottocategoria'
    })

#--------------------------------------------------------------------------------------------------------------------
def elimina_sottocategoria(request, id):
    sotto = get_object_or_404(SottoCategoria, id=id)
    sotto.delete()
    return redirect('admin-sottocategoria')

#-----------------------------------------------------------------------------------------------------------------
#                  dati negozio
#------------------------------------------------------------------------------------------------------------------

def dati_negozio_admin_view(request):
    contatti = ContattiBrand.objects.last()
    tutti_contatti = ContattiBrand.objects.all()
    return render(request, 'amministratore/dati_negozio_lista.html', {
        'contatti': contatti,
        'tutti_contatti': tutti_contatti,
    })
#------------------------------------------------------------------------------------------------------------
def modifica_dati_negozio(request):
    ultimo = ContattiBrand.objects.last()
    form = ContattiBrandForm(request.POST or None, request.FILES or None, instance=ultimo)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Dati negozio aggiornati con successo.")
            return redirect('dati_negozio_admin')
    return render(request, 'amministratore/modifica_dati_negozio.html', {'form': form})
#------------------------------------------------------------------------------------------------------------
def elimina_dati_negozio(request, id):
    dato = get_object_or_404(ContattiBrand, id=id)
    dato.delete()
    messages.warning(request, "Dato negozio eliminato.")
    return redirect('dati_negozio_admin')
#-------------------------------------------------------------------------------------------------------------
def usa_dati_negozio(request, id):
    dato = get_object_or_404(ContattiBrand, id=id)
    ContattiBrand.objects.exclude(id=id).delete()
    messages.info(request, "Questo dato negozio è stato impostato come principale.")
    return redirect('dati_negozio_admin')
#-------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------
@user_passes_test(is_admin)
def pagine(request):
    return render(request, 'amministratore/pagine.html')

#---------------------------------------------------------------------------------------------------------------

@user_passes_test(is_admin)
def statistiche(request):
    return render(request, 'amministratore/statistiche.html')
#-----------------------------------------------------------------------------------------------------------------


from django.shortcuts import redirect

def redirect_admin_django(request):
    return redirect('/admin/')
#----------------------------------------------------------------------------------------------------------------
def check_session(request):
    from django.http import HttpResponse
    return HttpResponse(f"User: {request.user}, Last Activity: {request.session.get('last_activity')}")

#---------------------------------------------------------------------------------------
#                                      
#--------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------------
                #       magazzino entrate 
#--------------------------------------------------------------------------------------------------------------


from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from .forms import EntrataMagazzinoForm
from .models import EntrataMagazzino


@user_passes_test(is_admin)
def magazzino_entrate(request):
    form = EntrataMagazzinoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, '✅ Entrata registrata con successo.')
        return redirect('magazzino_entrate')

    query = request.GET.get('q', '')
    entrate = EntrataMagazzino.objects.all().order_by('-data_arrivo')

    if query:
        entrate = entrate.filter(
            Q(codice_prodotto__icontains=query) | Q(nome_prodotto__icontains=query)
        )

    return render(request, 'amministratore/magazzino_entrate.html', {
        'form': form,
        'entrate': entrate,
        'query': query,
    })


#-------------------------------------------------------------------------------------------------------------


@user_passes_test(is_admin)
def arrivo_magazzino_view(request):
    form = EntrataMagazzinoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        entrata = form.save(commit=False)

        # Recupera info da Prodotto per completare i campi facoltativi
        try:
            from core.models import Prodotto
            prodotto = Prodotto.objects.get(codice_prodotto=entrata.codice_prodotto)

            if not entrata.nome_prodotto:
                entrata.nome_prodotto = prodotto.nome
            if not entrata.codice_magazzino:
                entrata.codice_magazzino = prodotto.codice_magazzino
            if not entrata.prezzo_con_iva or entrata.prezzo_con_iva == 0:
                entrata.prezzo_con_iva = prodotto.prezzo
        except Prodotto.DoesNotExist:
            pass  # Lascia i campi come sono

        entrata.save()
        messages.success(request, '✅ Entrata registrata.')
        return redirect('arrivo-magazzino')

    entrate = EntrataMagazzino.objects.all().order_by('-data_arrivo')
    return render(request, 'arrivi_magazzino.html', {'form': form, 'entrate': entrate})



#-------------------------------------------------------------------------------------------------------------

@user_passes_test(is_admin)
def modifica_entrata_magazzino(request, pk):
    entrata = get_object_or_404(EntrataMagazzino, pk=pk)
    form = EntrataMagazzinoForm(request.POST or None, instance=entrata)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, '✅ Entrata aggiornata con successo.')
        return redirect('magazzino_entrate')

    return render(request, 'amministratore/modifica_entrata.html', {
        'form': form,
        'titolo': 'Modifica Entrata'
    })


    
#--------------------------------------------------------------------------------------------------------------
@user_passes_test(is_admin)
def elimina_entrata_magazzino(request, pk):
    entrata = get_object_or_404(EntrataMagazzino, pk=pk)
    entrata.delete()
    messages.success(request, '❌ Entrata eliminata con successo.')
    return redirect('magazzino_entrate')

#---------------------------------------------------------------------------------------------------------------

def arrivo_magazzino_view(request):
    if request.method == 'POST':
        form = EntrataMagazzinoForm(request.POST)
        if form.is_valid():
            prodotto = form.cleaned_data['prodotto']
            entrata = form.save(commit=False)

            # Inserisce dati dal prodotto selezionato
            entrata.codice_prodotto = prodotto.codice_prodotto
            entrata.codice_magazzino = prodotto.codice_magazzino
            entrata.nome_prodotto = prodotto.nome
            entrata.prezzo_con_iva = prodotto.prezzo

            entrata.save()  # chiama anche save personalizzato che aggiorna disponibilità
            messages.success(request, f"✅ Arrivo salvato e disponibilità aggiornata per {prodotto.nome}.")
            return redirect('arrivo-magazzino')
    else:
        form = EntrataMagazzinoForm()

    entrate = EntrataMagazzino.objects.all().order_by('-data_arrivo')
    return render(request, 'arrivi_magazzino.html', {'form': form, 'entrate': entrate})



from django.http import JsonResponse

@user_passes_test(is_admin)
def toggle_aggiunto(request, pk):
    if request.method == 'POST':
        entrata = get_object_or_404(EntrataMagazzino, pk=pk)
        entrata.aggiunto = not entrata.aggiunto
        entrata.save()
        return JsonResponse({'success': True, 'aggiunto': entrata.aggiunto})
    return JsonResponse({'success': False}, status=400)


from core.models import Prodotto
from django.http import JsonResponse

@user_passes_test(is_admin)
def get_prodotto_info(request):
    codice = request.GET.get('codice_prodotto')
    try:
        prodotto = Prodotto.objects.get(codice_prodotto=codice)
        return JsonResponse({
            'nome_prodotto': prodotto.nome,
            'codice_magazzino': prodotto.codice_magazzino,
            'prezzo_con_iva': str(prodotto.prezzo)
        })
    except Prodotto.DoesNotExist:
        return JsonResponse({}, status=404)


#---------------------------------------------------------------------------------------------------------------
#                MAGAZZINO     Prodotto in magazzino
#---------------------------------------------------------------------------------------------------------------

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from core.models import Prodotto

@user_passes_test(is_admin)
def magazzino(request):
    prodotti = Prodotto.objects.all().order_by('-id')  # Ordina i prodotti dal più recente

    context = {
        'prodotti': prodotti
    }
    return render(request, 'amministratore/magazzino.html', context)


from django.db.models import Q
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas

@user_passes_test(is_admin)
def situazione_magazzino(request):
    query = request.GET.get('q', '')
    prodotti = Prodotto.objects.all()

    if query:
        prodotti = prodotti.filter(
            Q(codice_prodotto__icontains=query) | Q(nome__icontains=query)
        )

    if 'export_pdf' in request.GET:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, "Situazione Magazzino")

        y = 780
        for prodotto in prodotti:
            riga = f"{prodotto.codice_prodotto} - {prodotto.nome} - Disp: {prodotto.disponibilita}"
            p.drawString(50, y, riga)
            y -= 20
            if y < 40:
                p.showPage()
                y = 800

        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='situazione_magazzino.pdf')

    return render(request, 'amministratore/situazione_magazzino.html', {'prodotti': prodotti, 'query': query})

  


from django.http import FileResponse
from reportlab.pdfgen import canvas
import io

@user_passes_test(is_admin)
def esporta_magazzino_pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 12)
    p.drawString(200, 820, "📦 Situazione Completa Magazzino")

    prodotti = Prodotto.objects.all().order_by('nome')
    y = 790

    for prodotto in prodotti:
        line = f"{prodotto.codice_prodotto} - {prodotto.nome} | Disp: {prodotto.disponibilita} | Prezzo: € {prodotto.prezzo:.2f}"
        p.drawString(40, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 800

    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='magazzino_completo.pdf')


#------------------------------------------------------------------------------------------------------

def is_admin(user):
    return user.is_authenticated and user.is_staff
#-----------------------------------------------------------------------------------------------

def aggiungi_prodotto(request):
    if request.method == 'POST':
        form = ProdottoForm(request.POST, request.FILES)
        if form.is_valid():
            prodotto = form.save(commit=False)
            prodotto.save()
            messages.success(request, '✅ Prodotto salvato correttamente.')
            return redirect('aggiungi_prodotto')
        else:
            messages.error(request, '❌ Form non valido.')
    else:
        form = ProdottoForm()
        return render(request, 'amministratore/aggiungi_prodotto.html', {'form': form})
#-------------------------------------------------------------------------------------------------

@user_passes_test(is_admin)
def modifica_prodotto(request, pk):
    prodotto = get_object_or_404(Prodotto, pk=pk)

    if request.method == 'POST':
        form = ProdottoForm(request.POST, request.FILES, instance=prodotto)

        # Blocca i campi da non modificare anche in POST
        form.fields['codice_magazzino'].disabled = True
        form.fields['colorazioni'].widget = ColoriPreviewWidget(COLORI_NOMI)

        if form.is_valid():
            codice_nuovo = form.cleaned_data['codice_prodotto']
            if Prodotto.objects.filter(codice_prodotto=codice_nuovo).exclude(pk=prodotto.pk).exists():
                messages.error(request, "❌ Codice prodotto già esistente. Modifica annullata.")
            else:
                form.save()
                messages.success(request, "✅ Prodotto aggiornato con successo.")
                return redirect('admin-magazzino')
    else:
        form = ProdottoForm(instance=prodotto)
        form.fields['codice_magazzino'].disabled = True
        form.fields['colorazioni'].widget = ColoriPreviewWidget(COLORI_NOMI)

    return render(request, 'amministratore/form_prodotto.html', {
        'form': form,
        'titolo': 'Modifica Prodotto'
    })

#-------------------------------------------------------------------------------------------------------------------

@user_passes_test(is_admin)
def elimina_prodotto(request, pk):
    prodotto = get_object_or_404(Prodotto, pk=pk)
    prodotto.delete()
    messages.success(request, '✅ Prodotto eliminato con successo.')
    return redirect('magazzino_entrate')  # <-- CORRETTO


from .models import EntrataMagazzino
entrate = EntrataMagazzino.objects.all()
#----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------
#        MAGAZZINO       USCITE
#--------------------------------------------------------------------------------------------------------------

@user_passes_test(is_admin)
def magazzino_uscite(request):
    return render(request, 'amministratore/magazzino_uscite.html')

#----------------------------------------------------------------------------------------------------------------
@user_passes_test(is_admin)
def magazzino_uscite(request):
    prodotti_ordinati = OrdineItem.objects.select_related('prodotto', 'ordine', 'ordine__cliente')
    return render(request, 'amministratore/magazzino_uscite.html', {
        'prodotti_ordinati': prodotti_ordinati
    })

#---------------------------------------------------------------------------------------
#                         ticket ----- messaggi 
#---------------------------------------------------------------------------------------

@user_passes_test(is_admin)
def ticket_aperti(request):
    return render(request, 'amministratore/ticket_aperti.html')
#-----------------------------------------------------------------------------------------------------------
@user_passes_test(is_admin)
def ticket_aperti(request):
    ticket_list = Reclamo.objects.all().order_by('-data_invio')  # usa 'data_invio' corretto
    return render(request, 'amministratore/ticket_aperti.html', {'ticket_list': ticket_list})
#---------------------------------------------------------------------------------------------------------------

# TOGGLE STATO (APRI/CHIUDI)
@csrf_exempt
def toggle_stato_ticket(request, ticket_id):
    if request.method == 'POST':
        try:
            ticket = Reclamo.objects.get(id=ticket_id)
            ticket.stato = 'Chiuso' if ticket.stato == 'Aperto' else 'Aperto'
            ticket.save()
            return JsonResponse({'success': True, 'stato': ticket.stato})
        except Reclamo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ticket non trovato'})
    return JsonResponse({'success': False, 'error': 'Richiesta non valida'})

#---------------------------------------------------------------------------------------------------------------
# VISUALIZZA DETTAGLI TICKET
def visualizza_ticket(request, numero_ticket):
    ticket = get_object_or_404(Reclamo, numero_ticket=numero_ticket)
    return render(request, 'amministratore/ticket_dettaglio.html', {'ticket': ticket})

#-------------------------------------------------------------------------------------------------------------
# ELIMINA TICKET
@csrf_exempt
def elimina_ticket(request, ticket_id):
    if request.method == 'POST':
        try:
            ticket = Reclamo.objects.get(id=ticket_id)
            ticket.delete()
            return JsonResponse({'success': True})
        except Reclamo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ticket non trovato'})
    return JsonResponse({'success': False, 'error': 'Richiesta non valida'})

#-----------------------------------------------------------------------------------------------------------------


@user_passes_test(is_admin)
def admin_ticket(request):
    return render(request, 'amministratore/ticket_aperti.html')  # ✅ No


#------------------------------------------------------------------------------------------------------
#                       messaggi
#-------------------------------------------------------------------------------------------------------

@user_passes_test(is_admin)
def admin_messaggi(request):
    messaggi = MessaggioContatto.objects.all().order_by('-data_invio')
    return render(request, 'core/admin_messaggi.html', {'messaggi': messaggi})

#-----------------------------------------------------------------------------------------------------------------
@user_passes_test(is_admin)
def rispondi_messaggio(request, id):
    messaggio = get_object_or_404(MessaggioContatto, id=id)
    messaggio.letto = True
    messaggio.save()

    if request.method == 'POST':
        risposta = request.POST.get('risposta')
        send_mail(
            subject=f"Risposta al tuo messaggio: {messaggio.oggetto}",
            message=risposta,
            from_email='tuo@email.it',  # Cambia con la tua email
            recipient_list=[messaggio.email],
            fail_silently=False,
        )
        messages.success(request, "Risposta inviata con successo.")
        return redirect('admin-messaggi')

    return render(request, 'core/rispondi_messaggio.html', {'messaggio': messaggio})

#-------------------------------------------------------------------------------------------------------------------


@user_passes_test(is_admin)
def admin_rispondi(request, messaggio_id):
    messaggio = get_object_or_404(MessaggioContatto, id=messaggio_id)

    if request.method == 'POST':
        oggetto_risposta = request.POST.get('oggetto')
        testo_risposta = request.POST.get('risposta')
        allegato_risposta = request.FILES.get('allegato')

        # Invia email
        email = EmailMessage(
            subject=oggetto_risposta,
            body=testo_risposta,
            from_email='d.marmora0@gmail.com',
            to=[messaggio.email],
        )

        if allegato_risposta:
            email.attach(allegato_risposta.name, allegato_risposta.read(), allegato_risposta.content_type)

        try:
            email.send()
            messages.success(request, "Risposta inviata con successo.")
            messaggio.letto = True
            messaggio.save()
        except Exception as e:
            messages.error(request, f"Errore nell'invio della risposta: {e}")

        return redirect('admin-messaggi')

#-------------------------------------------------------------------------------------------------------------------

@user_passes_test(is_admin)
def admin_elimina_messaggio(request, messaggio_id):
    messaggio = get_object_or_404(MessaggioContatto, id=messaggio_id)
    messaggio.delete()
    messages.success(request, "Messaggio eliminato con successo.")
    return redirect('admin-messaggi')  # torna alla lista dei messaggi


#----------------------------------------------------------------------------------------
#                   Pagina informativa 
#------------------------------------------------------------------------------------------


class PaginaInformativaForm(forms.ModelForm):
    class Meta:
        model = PaginaInformativa
        fields = ['titolo', 'slug', 'contenuto_testo', 'immagine', 'video', 'pdf', 'mostra_pdf']

#---------------------------------------------------------------------------------------------------------------------
def lista_pagine(request):
    pagine = PaginaInformativa.objects.all()
    return render(request, 'amministratore/pagine.html', {'pagine': pagine})

#--------------------------------------------------------------------------------------------------------------------

def modifica_pagina(request, slug):
    pagina = get_object_or_404(PaginaInformativa, slug=slug)
    if request.method == 'POST':
        form = PaginaInformativaForm(request.POST, request.FILES, instance=pagina)
        if form.is_valid():
            form.save()
            return redirect('admin-dashboard')
    else:
        form = PaginaInformativaForm(instance=pagina)

    return render(request, 'amministratore/modifica_pagina.html', {'form': form, 'pagina': pagina})

#------------------------------------------------------------------------------------------------------------------

def aggiungi_pagina(request):
    if request.method == 'POST':
        form = PaginaInformativaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_pagine')
    else:
        form = PaginaInformativaForm()
    return render(request, 'amministratore/aggiungi_pagina.html', {'form': form})

#----------------------------------------------------------------------------------------------------------------


def rimuovi_pagina(request, slug):
    pagina = get_object_or_404(PaginaInformativa, slug=slug)
    if request.method == 'POST':
        pagina.delete()
        messages.success(request, 'Pagina rimossa con successo.')
        return redirect('lista_pagine')
    return render(request, 'amministratore/conferma_rimozione.html', {'pagina': pagina})

#-----------------------------------------------------------------------------------------------------------------

def pagina_dinamica(request, slug):
    pagina = get_object_or_404(PaginaInformativa, slug=slug)
    return render(request, 'core/pagina_dinamica.html', {'pagina': pagina})

#-------------------------------------------------------------------------------------------------------------
#                   Profilo
#--------------------------------------------------------------------------------------------------------------

@user_passes_test(is_admin)
def profilo_admin_placeholder(request):
    return render(request, 'amministratore/profilo.html')  # ma meglio evitarla
#-----------------------------------------------------------------------------------------------------------------
def lista_utenti(request):
    utenti = UserProfile.objects.all()
    return render(request, 'amministratore/profilo.html', {'utenti': utenti})
#----------------------------------------------------------------------------------------------------------------

def modifica_utente(request, pk):
    profilo = get_object_or_404(UserProfile, pk=pk)
    
    if request.method == 'POST':
        form = ModificaProfiloForm(request.POST, instance=profilo)
        if form.is_valid():
            form.save()
            return redirect('lista_utenti')
    else:
        form = ModificaProfiloForm(instance=profilo)

    return render(request, 'amministratore/modifica_utente.html', {'form': form})
#----------------------------------------------------------------------------------------------------------------

def elimina_utente(request, id):
    profilo = get_object_or_404(UserProfile, id=id)
    user = profilo.user
    profilo.delete()
    user.delete()
    messages.success(request, "Utente eliminato con successo.")
    return redirect('admin-profilo')

#-------------------------------------------------------------------------------------------------------------------

@csrf_exempt
def modifica_utente_ajax(request, id):
    if request.method == 'POST':
        try:
            profilo = UserProfile.objects.get(id=id)
            profilo.nome = request.POST.get('nome')
            profilo.cognome = request.POST.get('cognome')
            profilo.indirizzo = request.POST.get('indirizzo')
            profilo.civico = request.POST.get('civico')
            profilo.cap = request.POST.get('cap')
            profilo.citta = request.POST.get('citta')
            profilo.provincia = request.POST.get('provincia')
            profilo.codice_fiscale = request.POST.get('codice_fiscale')
            profilo.telefono = request.POST.get('telefono')
            profilo.save()

            # aggiorna anche l'email dell'utente
            profilo.user.email = request.POST.get('email')
            profilo.user.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Metodo non consentito'})

#------------------------------------------------------------------------------------------------------
#                ordini
#-------------------------------------------------------------------------------------------------------

# ❌ questa non passa nulla
@user_passes_test(is_admin)
def ordini(request):
    return render(request, 'amministratore/ordini.html')

from core.models import Ordine
from django.contrib.auth.decorators import user_passes_test
#--------------------------------------------------------------------------------------------------------------------
from django.contrib.auth.decorators import user_passes_test
from core.models import Ordine

@user_passes_test(lambda u: u.is_superuser)  # o is_admin se lo usi
def lista_ordini(request):
    ordini = Ordine.objects.select_related('cliente') \
        .prefetch_related('ordineitem_set__prodotto') \
        .order_by('-pagato', '-data_creazione')  # Pagati prima, poi per data

    return render(request, 'amministratore/ordini.html', {'ordini': ordini})


#--------------------------------------------------------------------------------------------------------------------

def dettaglio_ordine_pdf(request, ordine_id):
    ordine = Ordine.objects.get(pk=ordine_id)
    template_path = 'amministratore/pdf_ordine.html'
    context = {'ordine': ordine}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ordine_{ordine_id}.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Errore nella generazione del PDF')
    return response
#------------------------------------------------------------------------------------------------------------------

def dettaglio_utente_ordini(request, ordine_id):
    ordine = get_object_or_404(Ordine, id=ordine_id)

    # Filtra tutti gli ordini dello stesso utente (anche non autenticato)
    if ordine.cliente:
        ordini_utente = Ordine.objects.filter(cliente=ordine.cliente)
    else:
        ordini_utente = Ordine.objects.filter(nome=ordine.nome, cognome=ordine.cognome, email=ordine.email)

    context = {
        'utente': ordine,
        'ordini_utente': ordini_utente
    }
    return render(request, 'amministratore/dettaglio_utente_ordini.html', context)
#------------------------------------------------------------------------------------------------------------------

def esporta_ordine_pdf(request, ordine_id):
    try:
        ordine = Ordine.objects.get(pk=ordine_id)
    except Ordine.DoesNotExist:
        return HttpResponse("Ordine non trovato.", status=404)

    # Recupera i contatti del brand (primo e unico oggetto)
    contatti = ContattiBrand.objects.first()

    template_path = 'amministratore/ordine_pdf.html'
    context = {
        'ordine': ordine,
        'contatti': contatti,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ordine_{ordine.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Errore nella generazione del PDF', status=500)

    return response


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from core.models import Ordine, OrdineItem

@staff_member_required
def elimina_ordine_non_pagato(request, ordine_id):
    ordine = get_object_or_404(Ordine, id=ordine_id)

    if ordine.pagato:
        messages.error(request, "❌ Questo ordine è già stato pagato e non può essere eliminato.")
        return redirect('lista_ordini')

    # Ripristina la disponibilità per ogni prodotto dell'ordine
    for item in ordine.ordineitem_set.all():
        prodotto = item.prodotto
        prodotto.disponibilita += item.quantita
        prodotto.save()

    # Elimina l'ordine
    ordine.delete()
    messages.success(request, "✅ Ordine non pagato eliminato correttamente. Le quantità sono state ripristinate.")
    return redirect('lista_ordini')



#-------------------------------------------------------------------------------------------------------------
#             brand
#-------------------------------------------------------------------------------------------------------------------------



def vedi_brand(request, id):
    brand = get_object_or_404(Brand, id=id)
    return render(request, 'amministratore/vedi_brand.html', {'brand': brand})
#-------------------------------------------------------------------------------------------------------------------
def modifica_brand(request, id):
    brand = get_object_or_404(Brand, id=id)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            return redirect('vedi_brand', id=brand.id)
    else:
        form = BrandForm(instance=brand)
    return render(request, 'amministratore/modifica_brand.html', {'form': form})

#-------------------------------------------------------------------------------------------------------------------------------------

 # assicurati che HomeElemento sia importato

def gestione_home(request):
    cards = HomeCard.objects.all()
    banners = HomeBanner.objects.all()
    elementi = HomeElemento.objects.all()  # <-- AGGIUNGI QUESTO
    return render(request, 'amministratore/gestione_home.html', {
        'cards': cards,
        'banners': banners,
        'elementi': elementi,  # <-- PASSALO AL TEMPLATE
    })

#-----------------------------------------------------------------------------------------------------------------
def modifica_card(request, card_id):
    card = get_object_or_404(HomeCard, pk=card_id)
    if request.method == 'POST':
        form = HomeCardForm(request.POST, request.FILES, instance=card)
        if form.is_valid():
            form.save()
            return redirect('gestione_home')
    else:
        form = HomeCardForm(instance=card)
    return render(request, 'amministratore/modifica_card.html', {'form': form})
#------------------------------------------------------------------------------------------------------------------






def modifica_banner(request, banner_id):
    banner = get_object_or_404(HomeBanner, pk=banner_id)
    
    if request.method == 'POST':
        form = HomeBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, "Banner modificato con successo.")
            return redirect('gestione_home')
    else:
        form = HomeBannerForm(instance=banner)

    return render(request, 'amministratore/modifica_banner.html', {
        'form': form,
        'banner': banner,
    })



#-----------------------------------------------------------------------------------------------------------------

def aggiungi_card(request):
    if request.method == 'POST':
        form = HomeCardForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Card aggiunta con successo.")
            return redirect('gestione_home')
    else:
        form = HomeCardForm()
    return render(request, 'amministratore/aggiungi_card.html', {'form': form})

#-----------------------------------------------------------------------------------------------------------------
# ELIMINA CARD
def elimina_card(request, card_id):
    card = get_object_or_404(HomeCard, pk=card_id)
    if request.method == 'POST':
        card.delete()
        messages.success(request, "Card eliminata con successo.")
        return redirect('gestione_home')
    return render(request, 'amministratore/conferma_elimina_card.html', {'card': card})
#-----------------------------------------------------------------------------------------------------------------

# AGGIUNGI BANNER
def aggiungi_banner(request): 
    if request.method == 'POST':
        form = HomeBannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Banner aggiunto con successo.")
            return redirect('gestione_home')
    else:
        form = HomeBannerForm()
    return render(request, 'amministratore/aggiungi_banner.html', {'form': form})

#------------------------------------------------------------------------------------------------------------------

# ELIMINA BANNER
def elimina_banner(request, banner_id):
    banner = get_object_or_404(HomeBanner, pk=banner_id)
    if request.method == 'POST':
        banner.delete()
        messages.success(request, "Banner eliminato con successo.")
        return redirect('gestione_home')
    return render(request, 'amministratore/conferma_elimina_banner.html', {'banner': banner})

#-----------------------------------------------------------------------------------------------------------------

def gestione_home(request):
    cards = HomeCard.objects.all()
    banners = HomeBanner.objects.all()
    elementi = HomeElemento.objects.all()
    return render(request, 'amministratore/gestione_home.html', {
        'cards': cards,
        'banners': banners,
        'elementi': elementi,
    })
#-----------------------------------------------------------------------------------------------------------
def aggiungi_elemento(request):
    if request.method == 'POST':
        form = HomeElementoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gestione_home')
    else:
        form = HomeElementoForm()
    return render(request, 'amministratore/aggiungi_elemento.html', {'form': form})

#---------------------------------------------------------------------------------------------------------------
def modifica_elemento(request, elemento_id):
    elemento = get_object_or_404(HomeElemento, pk=elemento_id)
    if request.method == 'POST':
        form = HomeElementoForm(request.POST, request.FILES, instance=elemento)
        if form.is_valid():
            form.save()
            return redirect('gestione_home')
    else:
        form = HomeElementoForm(instance=elemento)
    return render(request, 'amministratore/modifica_elemento.html', {'form': form})
#----------------------------------------------------------------------------------------------------------------

def elimina_elemento(request, elemento_id):
    elemento = get_object_or_404(HomeElemento, pk=elemento_id)
    if request.method == 'POST':
        elemento.delete()
        return redirect('gestione_home')
    return render(request, 'amministratore/elimina_elemento.html', {'elemento': elemento})

#------------------------------------------------------------------------------------------------------------

def gestione_reclami(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('stato_') or key.startswith('esito_') or key.startswith('risposta_') or key.startswith('messaggio_'):
                try:
                    _, field, rid = key.split('_')
                    reclamo = Reclamo.objects.get(id=rid)

                    if field == 'stato':
                        reclamo.stato = value
                    elif field == 'esito':
                        reclamo.esito = value
                    elif field == 'messaggio':
                        reclamo.messaggio = value
                    elif field == 'risposta':
                        reclamo.risposta_admin = value

                        # ✅ Se è stata aggiunta o modificata la risposta, invia email all'utente
                        subject = f"Risposta al tuo reclamo #{reclamo.numero_ticket}"
                        message = f"""
Gentile {reclamo.nome} {reclamo.cognome},

Hai ricevuto una risposta al tuo reclamo inviato in data {reclamo.data_invio.strftime('%d/%m/%Y')}.

📝 Oggetto: {reclamo.oggetto}
📩 Messaggio: {reclamo.messaggio}

Risposta dell'amministratore:
{reclamo.risposta_admin}

Grazie per averci contattato.
                        """.strip()

                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [reclamo.email],
                            fail_silently=False,
                        )

                    reclamo.data_risposta = now()
                    reclamo.save()
                except:
                    continue

        return redirect('gestione_reclami')  # ✅ Giusto, se la tua URL si chiama così # ✅ Nome corretto nella tua urls.py

    reclami = Reclamo.objects.all().order_by('-data_invio')
    return render(request, 'amministratore/ticket_aperti.html', {
        'reclami': reclami,
        'stato_choices': STATO_CHOICES,
        'esito_choices': ESITO_CHOICES,
    })
#----------------------------------------------------------------------------------------------------------------

def dettaglio_reclamo(request, id):
    reclamo = get_object_or_404(Reclamo, id=id)
    return render(request, 'amministratore/dettaglio_reclamo.html', {'reclamo': reclamo})
#---------------------------------------------------------------------------------------------------------------

def rispondi_reclamo(request, id):
    reclamo = get_object_or_404(Reclamo, id=id)

    if request.method == 'POST':
        risposta = request.POST.get('risposta_admin')
        
        if risposta:  # ← Previene il salvataggio nullo
            reclamo.risposta_admin = risposta
            reclamo.data_risposta = now()
            reclamo.save()

            # Invia l’email
            subject = f"Risposta al tuo reclamo #{reclamo.numero_ticket}"
            message = f"""
Gentile {reclamo.nome} {reclamo.cognome},

Hai ricevuto una risposta al tuo reclamo inviato in data {reclamo.data_invio.strftime('%d/%m/%Y')}.

📝 Oggetto: {reclamo.oggetto}
📩 Messaggio: {reclamo.messaggio}

Risposta dell'amministratore:
{reclamo.risposta_admin}

Grazie per averci contattato.
            """.strip()

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [reclamo.email],
                fail_silently=False,
            )

            return redirect('gestione_reclami')
        else:
            return render(request, 'amministratore/rispondi_reclamo.html', {
                'reclamo': reclamo,
                'errore': 'La risposta non può essere vuota.',
            })

    return render(request, 'amministratore/rispondi_reclamo.html', {'reclamo': reclamo})


#---------------------------------------------------------------------------------------------------------------------------

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def lista_cookie(request):
    cookies = CookieConsent.objects.all().order_by('-data')
    return render(request, 'amministratore/cookie_list.html', {'cookies': cookies})
#--------------------------------------------------------------------------------------------------------------------------------
@login_required
@user_passes_test(is_admin)
def elimina_cookie(request, pk):
    cookie = get_object_or_404(CookieConsent, pk=pk)
    cookie.delete()
    return redirect('lista_cookie')

#------------sconto--------------------------------------------------------------------------------------------------

def gestione_spese_e_sconti(request):
    # Recupera o crea il prezzo di spedizione
    spedizione, _ = PrezzoSpedizione.objects.get_or_create(
    pk=1,
    defaults={
        'prezzo': 0.00  # oppure un valore adeguato
    }
)
    spedizione_form = PrezzoSpedizioneForm(request.POST or None, instance=spedizione)

    if request.method == 'POST' and 'salva_spedizione' in request.POST:
        if spedizione_form.is_valid():
            spedizione_form.save()
            messages.success(request, "Prezzo spedizione aggiornato.")
            return redirect('gestione_spese_sconti')

    # Gestione invio codice sconto
    sconto_form = CodiceScontoGeneraForm(request.POST or None)
    if request.method == 'POST' and 'invia_sconto' in request.POST:
        if sconto_form.is_valid():
            # ✅ Genera codice sconto casuale
            codice = get_random_string(length=10).upper()

            # ✅ Salva codice nel database
            sconto = sconto_form.save(commit=False)
            sconto.codice = codice
            sconto.save()

            # ✅ Invia email all'utente
            send_mail(
                subject='🎁 Hai ricevuto un Codice Sconto!',
                message=(
                    f"Ciao {sconto.utente.username},\n\n"
                    f"Hai ricevuto un codice sconto del {sconto.percentuale}%.\n"
                    f"Codice: {sconto.codice}\n"
                    f"Valido per {'più utilizzi' if sconto.multiuso else 'un solo utilizzo'}.\n\n"
                    f"Usalo subito sul nostro sito!"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[sconto.utente.email],
                fail_silently=False,
            )

            messages.success(request, "Codice sconto generato e inviato via email!")
            return redirect('gestione_spese_sconti')

    codici_sconto = CodiceSconto.objects.select_related('utente').all()

    return render(request, 'amministratore/gestione_spese_sconti.html', {
        'spedizione_form': spedizione_form,
        'sconto_form': sconto_form,
        'codici_sconto': codici_sconto,
    })
#-------------------------------------------------------------------------------------------------------------

# Aggiungi Contenuto
@login_required
def contenuti_add(request):
    if request.method == 'POST':
        form = ContenutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contenuti-lista')
    else:
        form = ContenutoForm()
    return render(request, 'amministratore/contenuti_add.html', {'form': form})
#-----------------------------------------------------------------------------------------------------------
# Aggiungi Richiesta
@login_required
def richieste_add(request):
    if request.method == 'POST':
        form = RichiestaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('richieste-lista')
    else:
        form = RichiestaForm()
    return render(request, 'amministratore/richieste_add.html', {'form': form})

#-------------------------------------------------------------------------------------------------------------

@login_required
def contenuti_modifica(request, pk):
    contenuto = Contenuto.objects.get(id=pk)
    if request.method == 'POST':
        form = ContenutoForm(request.POST, instance=contenuto)
        if form.is_valid():
            form.save()
            return redirect('contenuti-lista')
    else:
        form = ContenutoForm(instance=contenuto)
    return render(request, 'amministratore/contenuti_modifica.html', {'form': form})
#----------------------------------------------------------------------------------------------------------------
# MODIFICA Richiesta
@login_required
def richieste_modifica(request, pk):
    richiesta = Richiesta.objects.get(id=pk)
    if request.method == 'POST':
        form = RichiestaForm(request.POST, instance=richiesta)
        if form.is_valid():
            form.save()
            return redirect('richieste-lista')
    else:
        form = RichiestaForm(instance=richiesta)
    return render(request, 'amministratore/richieste_modifica.html', {'form': form})

#---------------------------------------------------------------------------------------------------------------
# ELIMINA Contenuto
@login_required
def contenuti_elimina(request, pk):
    contenuto = Contenuto.objects.get(id=pk)
    contenuto.delete()
    return redirect('contenuti-lista')
#--------------------------------------------------------------------------------------------------------------
# ELIMINA Richiesta
@login_required
def richieste_elimina(request, pk):
    richiesta = Richiesta.objects.get(id=pk)
    richiesta.delete()
    return redirect('richieste-lista')
#-------------------------------------------------------------------------------------------------------------
# DASHBOARD Dati Home
@login_required
def dati_home(request):
    contenuti = Contenuto.objects.all()
    richieste = Richiesta.objects.all()
    log_entries = LogEvento.objects.all()
    return render(request, 'amministratore/dati_home.html', {
        'contenuti': contenuti,
        'richieste': richieste,
        'log_entries': log_entries,
    })
#---------------------------------------------------------------------------------------------------------
# DASHBOARD Globale
@login_required
def dashboard_globale(request):
    contenuti = Contenuto.objects.all()
    richieste = Richiesta.objects.all()
    log_entries = LogEvento.objects.all()
    return render(request, 'amministratore/dashboard_globale.html', {
        'contenuti': contenuti,
        'richieste': richieste,
        'log_entries': log_entries,
    })

# =============== CONTENUTI ===============---------------------------------------------------------------

@login_required
def contenuti_lista(request):
    contenuti = Contenuto.objects.order_by('-timestamp')
    return render(request, 'amministratore/contenuti_lista.html', {'contenuti': contenuti})
#-----------------------------------------------------------------------------------------------------------
@login_required
def contenuti_add(request):
    if request.method == 'POST':
        form = ContenutoForm(request.POST)
        if form.is_valid():
            Contenuto(
                titolo=form.cleaned_data['titolo'],
                contenuto_completo=form.cleaned_data['contenuto_completo'],
                url_pagina=form.cleaned_data['url_pagina']
            ).save()
            return redirect('contenuti-lista')
    else:
        form = ContenutoForm()
    return render(request, 'amministratore/contenuti_add.html', {'form': form})
#----------------------------------------------------------------------------------------------------------------
@login_required
def contenuti_modifica(request, pk):
    contenuto = Contenuto.objects.get(id=pk)
    if request.method == 'POST':
        form = ContenutoForm(request.POST)
        if form.is_valid():
            contenuto.titolo = form.cleaned_data['titolo']
            contenuto.contenuto_completo = form.cleaned_data['contenuto_completo']
            contenuto.url_pagina = form.cleaned_data['url_pagina']
            contenuto.save()
            return redirect('contenuti-lista')
    else:
        form = ContenutoForm(initial={
            'titolo': contenuto.titolo,
            'contenuto_completo': contenuto.contenuto_completo,
            'url_pagina': contenuto.url_pagina
        })
    return render(request, 'amministratore/contenuti_modifica.html', {'form': form})
#--------------------------------------------------------------------------------------------------------------
@login_required
def contenuti_elimina(request, pk):
    contenuto = Contenuto.objects.get(id=pk)
    contenuto.delete()
    return redirect('contenuti-lista')


# =============== RICHIESTE ===============------------------------------------------------------------

@login_required
def richieste_lista(request):
    richieste = Richiesta.objects.order_by('-data_richiesta')
    return render(request, 'amministratore/richieste_lista.html', {'richieste': richieste})

#-----------------------------------------------------------------------------------------------------------
@login_required
def richieste_add(request):
    if request.method == 'POST':
        form = RichiestaForm(request.POST)
        if form.is_valid():
            Richiesta(
                richiesta=form.cleaned_data['richiesta_completa'],
                email_utente=form.cleaned_data['utente_email'],
                data_richiesta=datetime.now()
            ).save()
            return redirect('richieste-lista')
    else:
        form = RichiestaForm()
    return render(request, 'amministratore/richieste_add.html', {'form': form})
#------------------------------------------------------------------------------------------------------------
@login_required
def richieste_modifica(request, pk):
    richiesta = Richiesta.objects.get(id=pk)
    if request.method == 'POST':
        form = RichiestaForm(request.POST)
        if form.is_valid():
            richiesta.richiesta_completa = form.cleaned_data['richiesta_completa']
            richiesta.utente_email = form.cleaned_data['utente_email']
            richiesta.save()
            return redirect('richieste-lista')
    else:
        form = RichiestaForm(initial={
            'richiesta_completa': richiesta.richiesta_completa,
            'utente_email': richiesta.utente_email
        })
    return render(request, 'amministratore/richieste_modifica.html', {'form': form})
#--------------------------------------------------------------------------------------------------------------
@login_required
def richieste_elimina(request, pk):
    richiesta = Richiesta.objects.get(id=pk)
    richiesta.delete()
    return redirect('richieste-lista')
#-----------------------------------------------------------------------------------------------------------------

@login_required
def log_lista(request):
    log_entries = InteractionLog.objects.all().order_by('-timestamp')
    return render(request, 'amministratore/log_lista.html', {'log_entries': log_entries})
#-----------------------------------------------------------------------------------------------------------------

@login_required
def dashboard_contenuti_mongo(request):
    contenuti = Contenuto.objects.order_by('-timestamp')
    return render(request, 'amministratore/dashboard_contenuti_mongo.html', {'contenuti': contenuti})
#------------------------------------------------------------------------------------------------------------------

@login_required
def dashboard_dati(request):
    # Connessione a MongoDB Cloud
    client = MongoClient('mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<dbname>?retryWrites=true&w=majority')
    db = client['nome_database']

    # Statistiche per ecommerce
    conteggio_prodotti = db['prodotti'].count_documents({})
    ordini_effettuati = db['ordini'].count_documents({})
    utenti_registrati = db['utenti'].count_documents({})
    recensioni_prodotti = db['recensioni'].count_documents({})
    prodotti_in_sconto = db['prodotti'].count_documents({"sconto": {"$gt": 0}})

    return render(request, 'amministratore/dashboard_dati.html', {
        'conteggio_prodotti': conteggio_prodotti,
        'ordini_effettuati': ordini_effettuati,
        'utenti_registrati': utenti_registrati,
        'recensioni_prodotti': recensioni_prodotti,
        'prodotti_in_sconto': prodotti_in_sconto,
    })

from django.utils.timezone import now
from django.db.models import Sum
from django.http import JsonResponse
from datetime import timedelta
from collections import defaultdict
from  core.models import OrdineItem

def vendite_annuali_view(request):
    data_fine = now().date()
    data_inizio = data_fine - timedelta(days=365)

    items = OrdineItem.objects.filter(pagato=True, data_acquisto__range=(data_inizio, data_fine))

    vendite = defaultdict(lambda: defaultdict(int))  # {data: {codice: quantità}}

    for item in items:
        giorno = item.data_acquisto.strftime('%Y-%m-%d')
        codice = item.prodotto.codice
        vendite[giorno][codice] += item.quantita

    etichette = sorted(vendite.keys())  # date ordinate
    codici_prodotti = set()
    for giorno in vendite:
        codici_prodotti.update(vendite[giorno].keys())

    datasets = []
    for codice in codici_prodotti:
        data_points = [vendite[giorno].get(codice, 0) for giorno in etichette]
        datasets.append({
            'label': codice,
            'data': data_points
        })

    return JsonResponse({
        'etichette': etichette,
        'datasets': datasets
    })




#-----------------------------------------------------------------------------------------------------------------

def admin_check(user):
    return user.is_superuser  # solo superuser può accedere
#-----------------------------------------------------------------------------------------------------------------

def admin_check(user):
    return user.is_staff
#----------------------------------------------------------------------------------------------------------------
@user_passes_test(admin_check)
def gestione_pagamenti(request):
    settings_pagamento, created = PaymentSettings.objects.get_or_create(id=1)

    if request.method == 'POST':
        settings_pagamento.stripe_secret_key = request.POST.get('stripe_secret_key')
        settings_pagamento.stripe_public_key = request.POST.get('stripe_public_key')
        settings_pagamento.paypal_client_id = request.POST.get('paypal_client_id')
        settings_pagamento.paypal_secret_key = request.POST.get('paypal_secret_key')
        settings_pagamento.paypal_mode = request.POST.get('paypal_mode')
        settings_pagamento.paypal_business_email = request.POST.get('paypal_business_email')
        settings_pagamento.scalapay_secret_key = request.POST.get('scalapay_secret_key')
        settings_pagamento.save()

        messages.success(request, "✅ Impostazioni di pagamento aggiornate con successo!")
        return redirect('gestione_pagamenti')

    return render(request, 'amministratore/gestione_pagamenti.html', {
        'settings_pagamento': settings_pagamento  # ✅ Questa riga deve essere completa e chiusa
    })

#-------------------------------------------------------------------------------------------------------------

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils.timezone import now
from django.db.models.functions import TruncDate
from datetime import timedelta, datetime
from core.models import Ordine, OrdineItem, Carrello

def get_carrelli_abbandonati_series(start_date, end_date):
    date_map = {}
    for i in range((end_date - start_date).days + 1):
        giorno = start_date + timedelta(days=i)
        date_map[giorno] = 0

    carrelli = Carrello.objects.filter(creato_il__range=(start_date, end_date))

    for c in carrelli:
        # ✅ Controlla se esiste un ordine collegato al carrello
        if not Ordine.objects.filter(carrello=c).exists():
            giorno = c.creato_il.date()
            if giorno in date_map:
                date_map[giorno] += 1

    etichette = [str(g) for g in sorted(date_map.keys())]
    valori = [date_map[g] for g in sorted(date_map.keys())]
    return etichette, valori

def dashboard_ai_admin(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        start_str = request.GET.get("start")
        end_str = request.GET.get("end")

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else (now().date() - timedelta(days=365))
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else now().date()
        except:
            start_date = now().date() - timedelta(days=365)
            end_date = now().date()

        ultime_24_ore = now() - timedelta(hours=24)
        ordini = Ordine.objects.all()
        ordini_ultime_ore = ordini.filter(data_creazione__gte=ultime_24_ore)
        ordini_pagati = ordini.filter(pagato=True)

        vendite_mese = ordini_ultime_ore.count()
        ordini_totali = ordini.count()
        clienti_totali = ordini.values('email').distinct().count()
        prodotti_venduti = OrdineItem.objects.aggregate(q=Sum('quantita'))['q'] or 0
        valore_totale_vendite = sum(o.get_totale() for o in ordini_pagati)

        visite_totali = 1000
        tasso_conversione = round((ordini_pagati.count() / visite_totali) * 100, 2) if visite_totali > 0 else 0
        carrelli_abbandonati = visite_totali - ordini_pagati.count()
        media_valore_ordine = round(valore_totale_vendite / ordini_pagati.count(), 2) if ordini_pagati.count() > 0 else 0

        top_prodotto = (
            OrdineItem.objects
            .values('prodotto__nome')
            .annotate(totale_venduto=Sum('quantita'))
            .order_by('-totale_venduto')
            .first()
        )
        nome_top_prodotto = top_prodotto['prodotto__nome'] if top_prodotto else "Nessun prodotto"
        quantita_top_prodotto = top_prodotto['totale_venduto'] if top_prodotto else 0

        # Vendite ultimi 7 giorni
        ultimi_7_giorni = now() - timedelta(days=7)
        vendite_per_giorno = (
            Ordine.objects
            .filter(data_creazione__gte=ultimi_7_giorni)
            .annotate(giorno=TruncDate('data_creazione'))
            .values('giorno')
            .annotate(totale=Sum('ordineitem__quantita'))
            .order_by('giorno')
        )
        etichette_giorni = [str(item['giorno']) for item in vendite_per_giorno]
        valori_giorni = [item['totale'] for item in vendite_per_giorno]

        # ✅ Prodotti venduti per codice_prodotto (campo corretto)
        vendite_prodotti = (
            OrdineItem.objects
            .filter(pagato=True)
            .values('prodotto__codice_prodotto')
            .annotate(quantita=Sum('quantita'))
            .order_by('prodotto__codice_prodotto')
        )
        prodotti_codici = [p['prodotto__codice_prodotto'] for p in vendite_prodotti]
        prodotti_quantita = [p['quantita'] for p in vendite_prodotti]

        # Carrelli abbandonati negli ultimi 365 giorni
        etichette_carrelli, valori_carrelli = get_carrelli_abbandonati_series(start_date, end_date)

        # 🔍 Analisi SWOT
        swot = {
            "Strengths": [],
            "Weaknesses": [],
            "Opportunities": [],
            "Threats": []
        }

        if tasso_conversione > 3.5:
            swot["Strengths"].append("Tasso di conversione superiore alla media.")
        if media_valore_ordine > 40:
            swot["Strengths"].append("Ordini medi di valore elevato.")
        if carrelli_abbandonati > ordini_totali:
            swot["Weaknesses"].append("Molti carrelli abbandonati rispetto agli ordini.")
        if vendite_mese < 100:
            swot["Weaknesses"].append("Vendite limitate nelle ultime 24 ore.")
        if clienti_totali < 500:
            swot["Opportunities"].append("Possibilità di espandere la clientela.")
        if prodotti_venduti > 800:
            swot["Opportunities"].append("Alta rotazione dei prodotti.")
        if tasso_conversione < 2:
            swot["Threats"].append("Conversione bassa rispetto alle visite.")
        if valore_totale_vendite < 10000:
            swot["Threats"].append("Fatturato insufficiente per sostenere la crescita.")

        data = {
            'vendite_mese': vendite_mese,
            'ordini_totali': ordini_totali,
            'clienti_totali': clienti_totali,
            'prodotti_venduti': prodotti_venduti,
            'valore_totale_vendite': valore_totale_vendite,
            'tasso_conversione': tasso_conversione,
            'carrelli_abbandonati': carrelli_abbandonati,
            'media_valore_ordine': media_valore_ordine,
            'nome_top_prodotto': nome_top_prodotto,
            'quantita_top_prodotto': quantita_top_prodotto,
            'etichette_giorni': etichette_giorni,
            'valori_giorni': valori_giorni,
            'prodotti_codici': prodotti_codici,
            'prodotti_quantita': prodotti_quantita,
            'etichette_carrelli_abbandonati': etichette_carrelli,
            'valori_carrelli_abbandonati': valori_carrelli,
            'swot': swot
        }

        return JsonResponse(data)

    return render(request, 'amministratore/dashboard_ai.html')



#--------------------------------------------------------------------------------------------------------------
# amministratore/views.py
def toggle_maintenance(request):
    if request.method == "POST":
        settings = SiteSettings.objects.first()
        if not settings:
            settings = SiteSettings.objects.create(maintenance_mode=False)
        settings.maintenance_mode = not settings.maintenance_mode
        settings.save()
    return redirect('admin-dashboard')  # Ritorna alla dashboard

#-----------------------------------------------------------------------------------------------------------------

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # non email
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect('admin-dashboard')  # vai alla dashboard admin
        else:
            return render(request, 'amministratore/maintenance.html', {'error': 'Accesso riservato solo agli amministratori.'})

    return render(request, 'amministratore/maintenance.html')


def calcola_totale_ordine(ordine):
    return sum(item.prodotto.prezzo * item.quantita for item in ordine.ordineitem_set.all())
#----------------------------------------------------------------------------------------------------------------

@staff_member_required
def lista_strisce_info(request):
    strisce = StrisciaInfo.objects.all()
    return render(request, 'amministratore/lista_strisce_info.html', {'strisce': strisce})
#----------------------------------------------------------------------------------------------------------------
@staff_member_required
def aggiungi_striscia(request):
    if request.method == 'POST':
        form = StrisciaInfoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_strisce_info')
    else:
        form = StrisciaInfoForm()
    return render(request, 'amministratore/aggiungi_striscia.html', {'form': form})
#-----------------------------------------------------------------------------------------------------------------
@staff_member_required
def modifica_striscia(request, pk):
    striscia = get_object_or_404(StrisciaInfo, pk=pk)
    if request.method == 'POST':
        form = StrisciaInfoForm(request.POST, instance=striscia)
        if form.is_valid():
            form.save()
            return redirect('lista_strisce_info')
    else:
        form = StrisciaInfoForm(instance=striscia)
    return render(request, 'amministratore/modifica_striscia.html', {'form': form, 'striscia': striscia})
#-------------------------------------------------------------------------------------------------------------------
@staff_member_required
def elimina_striscia(request, pk):
    striscia = get_object_or_404(StrisciaInfo, pk=pk)
    if request.method == 'POST':
        striscia.delete()
        return redirect('lista_strisce_info')
    return render(request, 'amministratore/elimina_striscia.html', {'striscia': striscia})

#--------------------------------------------------------------------------------------------------------
#          blog
#--------------------------------------------------------------------------------------------------------

@staff_member_required
def gestore_blog(request):
    articoli = ArticoloBlog.objects.all()
    commenti = CommentoBlog.objects.all()
    prodotti = ProdottoSuggerito.objects.all()
    banner = BannerInformativo.objects.all()
    return render(request, 'amministratore/gestore_blog.html', {
        'articoli': articoli,
        'commenti': commenti,
        'prodotti': prodotti,
        'banner': banner,
    })

#-------------------------------------------------------------------------------------------------------------

@staff_member_required
def elimina_commento_blog(request, id):
    commento = get_object_or_404(CommentoBlog, id=id)
    commento.delete()
    return redirect('gestore-blog')

#--------------------------------------------------------------------------------------------------

def articoli_blog_admin(request):
    articoli = ArticoloBlog.objects.all().order_by('-data_pubblicazione')
    return render(request, 'amministratore/gestione_articoli.html', {'articoli': articoli})
#------------------------------------------------------------------------------------------------------------
def articoli_blog_add(request):
    form = ArticoloBlogForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('admin-articoli-blog')
    return render(request, 'amministratore/articolo_form.html', {'form': form, 'titolo': 'Aggiungi Articolo'})
#-----------------------------------------------------------------------------------------------------------------
def articoli_blog_edit(request, pk):
    articolo = get_object_or_404(ArticoloBlog, pk=pk)
    form = ArticoloBlogForm(request.POST or None, request.FILES or None, instance=articolo)
    if form.is_valid():
        form.save()
        return redirect('admin-articoli-blog')
    return render(request, 'amministratore/articolo_form.html', {'form': form, 'titolo': 'Modifica Articolo'})
#------------------------------------------------------------------------------------------------------------------
def articoli_blog_delete(request, pk):
    articolo = get_object_or_404(ArticoloBlog, pk=pk)
    articolo.delete()
    return redirect('admin-articoli-blog')

#---------------------------------------------------------------------------------------------------

@staff_member_required
def gestione_articoli_blog(request):
    articoli = ArticoloBlog.objects.all()
    return render(request, 'amministratore/gestione_articoli.html', {'articoli': articoli})
#--------------------------------------------------------------------------------------------------------------

@staff_member_required
def gestione_commenti_blog(request):
    from blog.models import CommentoBlog
    commenti = CommentoBlog.objects.select_related('utente', 'post').all()
    return render(request, 'amministratore/gestione_commenti.html', {'commenti': commenti})
#---------------------------------------------------------------------------------------------------------------

@staff_member_required
def gestione_prodotti_blog(request):
    from blog.models import ProdottoSuggerito
    prodotti = ProdottoSuggerito.objects.select_related('autore').all()
    return render(request, 'amministratore/gestione_prodotti.html', {'prodotti': prodotti})

#-----------------------------------------------------------------------------------------------------------------

@staff_member_required
def gestione_banner_blog(request):
    banner_list = BannerInformativo.objects.all().order_by('-data_creazione')  # o filtrare visibili prima
    return render(request, 'amministratore/gestione_banner.html', {'banner_list': banner_list})

#-------------------------------------------------------------------------------------------------------------------

@staff_member_required
def gestione_banner_blog(request):
    banner_list = BannerInformativo.objects.all().order_by('-data_creazione')
    return render(request, 'amministratore/gestione_banner.html', {
        'banner_list': banner_list
    })

#-----------------------------------------------------------------------------------------------------------------
@staff_member_required
def banner_blog_add(request):
    if request.method == 'POST':
        form = BannerInformativoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin-banner-blog')
    else:
        form = BannerInformativoForm()

    colori = [
        ("Rosso", "#ff0000"), ("Verde", "#00ff00"), ("Blu", "#0000ff"),
        ("Giallo", "#ffff00"), ("Grigio", "#808080"), ("Nero", "#000000"),
        ("Bianco", "#ffffff"), ("Arancione", "#ffa500"), ("Viola", "#800080"),
        ("Ciano", "#00ffff")
    ]

    font = [
        ("Sans Serif", "sans-serif"), ("Serif", "serif"), ("Monospace", "monospace"),
        ("Arial", "Arial, sans-serif"), ("Helvetica", "Helvetica, sans-serif"),
        ("Georgia", "Georgia, serif"), ("Courier", "Courier, monospace"),
        ("Verdana", "Verdana, sans-serif"), ("Times", "'Times New Roman', serif"),
        ("Trebuchet", "'Trebuchet MS', sans-serif")
    ]

    return render(request, 'amministratore/banner_form.html', {
        'form': form,
        'titolo': 'Aggiungi Banner',
        'colori': colori,
        'font': font,
    })

#--------------------------------------------------------------------------------------------------------------
@staff_member_required
def banner_blog_edit(request, pk):
    banner = get_object_or_404(BannerInformativo, pk=pk)
    if request.method == 'POST':
        form = BannerInformativoForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            return redirect('admin-banner-blog')
    else:
        form = BannerInformativoForm(instance=banner)

    colori = [
        ("Rosso", "#ff0000"), ("Verde", "#00ff00"), ("Blu", "#0000ff"),
        ("Giallo", "#ffff00"), ("Grigio", "#808080"), ("Nero", "#000000"),
        ("Bianco", "#ffffff"), ("Arancione", "#ffa500"), ("Viola", "#800080"),
        ("Ciano", "#00ffff")
    ]

    font = [
        ("Sans Serif", "sans-serif"), ("Serif", "serif"), ("Monospace", "monospace"),
        ("Arial", "Arial, sans-serif"), ("Helvetica", "Helvetica, sans-serif"),
        ("Georgia", "Georgia, serif"), ("Courier", "Courier, monospace"),
        ("Verdana", "Verdana, sans-serif"), ("Times", "'Times New Roman', serif"),
        ("Trebuchet", "'Trebuchet MS', sans-serif")
    ]

    return render(request, 'amministratore/banner_form.html', {
        'form': form,
        'titolo': 'Modifica Banner',
        'colori': colori,
        'font': font,
    })
#------------------------------------------------------------------------------------------------------------

# 🗑️ ELIMINA
@staff_member_required
def banner_blog_delete(request, pk):
    banner = get_object_or_404(BannerInformativo, pk=pk)
    if request.method == 'POST':
        banner.delete()
        return redirect('admin-banner-blog')
    return render(request, 'amministratore/banner_delete_confirm.html', {'banner': banner})


#---------------------------------------------------------------------------------------------------------------

@staff_member_required
def aggiungi_prodotto_suggerito(request):
    if request.method == 'POST':
        form = ProdottoSuggeritoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Prodotto suggerito aggiunto con successo.")
            return redirect('admin-prodotti-blog')
    else:
        form = ProdottoSuggeritoForm()
    
    return render(request, 'amministratore/aggiungi_prodotto.html', {
        'form': form
    })

#---------------------------------------------------------------------------------------------------------

def elimina_uscita_magazzino(request, id):
    item = get_object_or_404(OrdineItem, id=id)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Prodotto eliminato con successo dall’uscita di magazzino.')
    return redirect('magazzino_uscite')  # assicurati che questa sia la name del path della pagina lista

#----------------------------------------------------------------------------------------------------------------

def elimina_ordine(request, ordine_id):
    ordine = get_object_or_404(Ordine, id=ordine_id)
    if request.method == "POST":
        ordine.delete()
        messages.success(request, "Ordine eliminato con successo.")
    return redirect('admin-ordini')  # o il nome corretto della pagina ordini

#-----------------------------------------------------------------------------------------------------------------

def test_email_smtp(request):
    try:
        send_mail(
            subject='🔐 Test SMTP',
            message='Questa è una email di test del sistema SMTP configurato nel tuo ecommerce.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        return JsonResponse({'success': True, 'message': 'Email inviata con successo ✅'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
#------------------------------------------------------------------------------------------------------------------
