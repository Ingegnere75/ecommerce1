EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'd.marmora0@gmail.com'
EMAIL_HOST_PASSWORD = 'emtv aexe tguu dmom'  # Password per app Gmail (non la password normale!)
DEFAULT_FROM_EMAIL = 'd.marmora0@gmail.com'
ADMINS = [('Admin', 'samadafilati@gmail.com')]


# Built-in
import json
import os
import re
import uuid
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from difflib import SequenceMatcher
from random import sample

# Third-party libraries
import openpyxl
import paypalrestsdk
import stripe
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from mongoengine.queryset.visitor import Q as MQ  # Q per MongoDB

# Django core
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from datetime import timezone

# App: Forms
from .forms import CodiceScontoForm, CheckoutForm

# App: Models
from .models import (
    Brand,
    CardSezione,
    Carrello,
    CarrelloItem,
    Categoria,
    CodiceSconto,
    ContattiBrand,
    CookieConsent,
    HomeBanner,
    HomeCard,
    HomeElemento,
    ImmaginePersonalizzata,
    Informativa,
    LayoutSalvato,
    MessaggioContatto,
    Ordine,
    OrdineItem,
    PaginaInformativa,
    PrezzoSpedizione,
    Prodotto,
    SottoCategoria,
)

# App: Extra
from .colori import COLORI_NOMI

# Altri moduli del progetto
from accounts.models import UserProfile, Wishlist
from amministratore.models import Contenuto, Richiesta, PaymentSettings
from blog.models import BannerInformativo
from contentcollector.models import ContentText
from contentcollector.utils import salva_contenuto
from core.services.logger_mongo import LogEvento
from logmanager.models import LogEntry
from requesttracker.models import UserRequest
from django.utils import timezone




#--------------------------------------------------------------------------------------------------------*--

def home(request):
    cards = HomeCard.objects.all()
    immagini_personalizzate = ImmaginePersonalizzata.objects.filter(attivo=True)
    prodotti = list(Prodotto.objects.all())
    elementi = HomeElemento.objects.all()

    # Dividi per zona
    elementi_hero = elementi.filter(zona='hero')
    elementi_center = elementi.filter(zona='center')
    elementi_bottom = elementi.filter(zona='bottom')
    elementi_custom = elementi.filter(zona='custom')

    # Recupera layout salvato dall’editor visuale
    layout_salvato = LayoutSalvato.objects.order_by('-salvato_il').first()
    layout_html = layout_salvato.contenuto if layout_salvato else ""

    # Banner divisi per zona
    banners_hero = HomeBanner.objects.filter(posizione='hero')
    banners_center = HomeBanner.objects.filter(posizione='center')
    banners_bottom = HomeBanner.objects.filter(posizione='bottom')

    # ✅ Banner Informativo attivo
    banner_informativo = BannerInformativo.objects.filter(visibile=True).order_by('-data_creazione').first()

    # Riempimento prodotti fino a 9
    if len(prodotti) < 9:
        prodotti += [None] * (9 - len(prodotti))

    # Recupera configurazione della sezione delle card (admin personalizzabile)
    card_sezione = CardSezione.objects.first()

    # ✅ Recupera il brand per il footer o per le card
    brand = Brand.objects.first()

    return render(request, 'core/home.html', {
        'cards': cards,
        'prodotti': prodotti,
        'immagini_personalizzate': immagini_personalizzate,
        'elementi_hero': elementi_hero,
        'elementi_center': elementi_center,
        'elementi_bottom': elementi_bottom,
        'elementi_custom': elementi_custom,
        'layout_salvato': layout_html,
        'banners_hero': banners_hero,
        'banners_center': banners_center,
        'banners_bottom': banners_bottom,
        'card_sezione': card_sezione,
        'brand': brand,  # ✅ brand usato nel template per mostrare info o creare link admin
        'banner': banner_informativo,  # ✅ aggiunto per il banner nella home
    })



#--------------------------------------------------------------------------------------------------


@staff_member_required
def editor_home(request):
    elementi = HomeElemento.objects.all()

    if request.method == 'POST':
        ordine = request.POST.getlist('ordine[]')
        for idx, elem_id in enumerate(ordine):
            HomeElemento.objects.filter(pk=int(elem_id)).update(ordine=idx)
        return redirect('editor_home')

    return render(request, 'core/editor_home.html', {
        'elementi': elementi
    })



#------categorie-------------------------------------------------------------------------------------------------

def categorie(request):
    categorie = Categoria.objects.all()
    return render(request, 'core/categorie.html', {
        'categorie': categorie
    })





def prodotti_per_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    sottocategorie = SottoCategoria.objects.filter(categoria=categoria)
    return render(request, 'core/prodotti_per_categoria.html', {
        'categoria': categoria,
        'sottocategorie': sottocategorie
    })



def dettaglio_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    sottocategorie = SottoCategoria.objects.filter(categoria=categoria)
    return render(request, 'core/dettaglio_categoria.html', {
        'categoria': categoria,
        'sottocategorie': sottocategorie
    })



#----------sottocategorie-----------------------------------------------------------------------------------

def sottocategorie_ajax(request, categoria_id):
    sottocategorie = SottoCategoria.objects.filter(categoria_id=categoria_id)
    html = render_to_string('core/partials/sottocategorie.html', {
        'sottocategorie': sottocategorie
    })
    return HttpResponse(html)


def prodotti_per_sottocategoria(request, slug):
    sottocategoria = get_object_or_404(SottoCategoria, slug=slug)
    prodotti = Prodotto.objects.filter(sottocategoria=sottocategoria)
    return render(request, 'core/prodotti_per_sottocategoria.html', {
        'sottocategoria': sottocategoria,
        'prodotti': prodotti
    })

#-----prodotti------------------------------------------------------------------------------------



def prodotti(request):
    categorie = Categoria.objects.all()
    tutti_prodotti = list(Prodotto.objects.all())

    prodotti_consigliati = []
    if tutti_prodotti:
        num = min(len(tutti_prodotti), 4)  # Mostra massimo 4 prodotti casuali
        prodotti_consigliati = sample(tutti_prodotti, num)

    return render(request, 'core/prodotti.html', {
        'categorie': categorie,
        'prodotti_consigliati': prodotti_consigliati,
    })



def dettaglio_prodotto_by_id(request, pk):
    prodotto = get_object_or_404(Prodotto, pk=pk)

    # Estrai colorazioni da nomi o HEX
    colori = []
    if prodotto.colorazioni:
        nomi_raw = [c.strip().lower() for c in prodotto.colorazioni.split(',') if c.strip()]
        for nome in nomi_raw:
            if nome.startswith('#'):
                colori.append(nome)
            else:
                colori.append(COLORI_NOMI.get(nome, '#000000'))  # fallback: nero

    # Prepara immagini extra
    immagini_extra = []
    for i in range(1, 9):
        img = getattr(prodotto, f'immagine_extra_{i}', None)
        alt = getattr(prodotto, f'altezza_extra_{i}', 300)
        lar = getattr(prodotto, f'larghezza_extra_{i}', 200)
        if img:
            immagini_extra.append({
                'src': img.url,
                'alt': alt,
                'lar': lar,
                'descrizione': getattr(prodotto, f'descrizione_{i}', ''),
                'altezza_descrizione': getattr(prodotto, f'altezza_descrizione_{i}', 300),
                'larghezza_descrizione': getattr(prodotto, f'larghezza_descrizione_{i}', 200),
            })

    # Prepara video
    video_extra = []
    for i in range(1, 3):
        vid = getattr(prodotto, f'video_{i}', None)
        alt = getattr(prodotto, f'altezza_video_{i}', 360)
        lar = getattr(prodotto, f'larghezza_video_{i}', 640)
        if vid:
            video_extra.append({
                'src': vid.url,
                'alt': alt,
                'lar': lar,
            })

    # Descrizioni extra
    descrizioni_extra = []
    for i in range(1, 9):
        testo = getattr(prodotto, f'descrizione_{i}', None)
        if testo:
            descrizioni_extra.append(testo)

    # ✅ Check wishlist (solo se autenticato)
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, prodotto=prodotto).exists()

    return render(request, 'core/dettaglio_prodotto.html', {
        'prodotto': prodotto,
        'colori': colori,
        'taglia': prodotto.taglia,
        'misura': prodotto.misura,
        'immagini_extra': immagini_extra,
        'video_extra': video_extra,
        'testo_aggiuntivo': prodotto.testo_aggiuntivo,
        'altezza_testo': prodotto.altezza_testo,
        'larghezza_testo': prodotto.larghezza_testo,
        'documento': prodotto.documento_1,
        'descrizioni_extra': descrizioni_extra,
        'in_wishlist': in_wishlist,  # 👈 usalo nel template
    })



#-----------carrello------------------------------------------------------------------------------


from decimal import Decimal
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from .models import Carrello, CarrelloItem, CodiceSconto, PrezzoSpedizione

def carrello(request):
    # Crea una sessione se non esiste
    sessione = request.session.session_key
    if not sessione:
        request.session.create()
        sessione = request.session.session_key

    # Recupera o crea il carrello associato alla sessione
    carrello, created = Carrello.objects.get_or_create(sessione=sessione)
    items = CarrelloItem.objects.filter(carrello=carrello)

    # Calcolo del totale prodotti
    totale_prodotti = sum(item.get_subtotale for item in items)

    # Calcolo della spedizione
    spedizione = PrezzoSpedizione.objects.first()
    prezzo_spedizione = spedizione.prezzo if spedizione else Decimal('0.00')
    if totale_prodotti >= Decimal('60.00'):
        prezzo_spedizione = Decimal('0.00')

    # Controllo codice sconto inserito nel form (POST)
    if request.method == 'POST':
        codice_input = request.POST.get('codice_sconto', '').strip()
        try:
            codice = CodiceSconto.objects.get(codice=codice_input, attivo=True)
            if not codice.scadenza or codice.scadenza >= timezone.now().date():
                request.session['codice_sconto'] = codice.codice
                messages.success(request, f"Codice sconto '{codice.codice}' applicato con successo!")
            else:
                messages.warning(request, "Codice sconto scaduto.")
        except CodiceSconto.DoesNotExist:
            messages.error(request, "Codice sconto non valido.")
        return redirect('carrello')  # evita riapplicazione su refresh

    # Recupero codice sconto dalla sessione
    codice_attivo = request.session.get('codice_sconto', None)
    sconto_percentuale = 0
    sconto = Decimal('0.00')

    if codice_attivo:
        try:
            codice = CodiceSconto.objects.get(codice=codice_attivo, attivo=True)
            if not codice.scadenza or codice.scadenza >= timezone.now().date():
                sconto_percentuale = codice.percentuale
                sconto = (totale_prodotti * Decimal(sconto_percentuale)) / Decimal('100')
            else:
                del request.session['codice_sconto']  # Rimuove il codice scaduto
        except CodiceSconto.DoesNotExist:
            del request.session['codice_sconto']  # Rimuove il codice non esistente

    # Calcolo del totale finale
    totale_finale = totale_prodotti - sconto + prezzo_spedizione

    return render(request, 'core/carrello.html', {
        'items': items,
        'totale_prodotti': totale_prodotti,
        'prezzo_spedizione': prezzo_spedizione,
        'sconto': sconto,
        'sconto_percentuale': sconto_percentuale,
        'codice_attivo': codice_attivo,
        'totale_finale': totale_finale,
    })



#----------------------------------------------------------------------------------------------

def aggiungi_al_carrello(request, prodotto_id):
    if request.method == 'POST':
        quantita = int(request.POST.get('quantita', 1))
        prodotto = get_object_or_404(Prodotto, id=prodotto_id)

        if quantita > prodotto.disponibilita:
            messages.error(request, f"Quantità non disponibile. Disponibili: {prodotto.disponibilita} pezzi.")
            return redirect('carrello')

        sessione = request.session.session_key
        if not sessione:
            request.session.create()
            sessione = request.session.session_key

        carrello, created = Carrello.objects.get_or_create(sessione=sessione)

        item, created = CarrelloItem.objects.get_or_create(carrello=carrello, prodotto=prodotto)

        if not created:
            nuova_quantita = item.quantita + quantita
            if nuova_quantita > prodotto.disponibilita:
                messages.error(request, f"Puoi aggiungere solo {prodotto.disponibilita - item.quantita} pezzi.")
                return redirect('carrello')
            item.quantita = nuova_quantita
        else:
            item.quantita = quantita

        item.save()
        messages.success(request, "Prodotto aggiunto al carrello.")
    
    return redirect('carrello')




def aggiorna_quantita(request, item_id):
    item = get_object_or_404(CarrelloItem, id=item_id)
    prodotto = item.prodotto

    if request.method == 'POST':
        try:
            nuova_quantita = int(request.POST.get('quantita', 1))
        except ValueError:
            messages.error(request, "Inserisci un numero valido per la quantità.")
            return redirect('carrello')

        if nuova_quantita < 1:
            messages.error(request, "La quantità deve essere almeno 1.")
            return redirect('carrello')

        if nuova_quantita > prodotto.disponibilita:
            messages.warning(
                request,
                f"Disponibilità limitata: massimo {prodotto.disponibilita} pezzi disponibili per '{prodotto.nome}'."
            )
            return redirect('carrello')

        item.quantita = nuova_quantita
        item.save()
        messages.success(request, f"Quantità aggiornata a {nuova_quantita} per '{prodotto.nome}'.")

    return redirect('carrello')





def rimuovi_dal_carrello(request, item_id):
    item = get_object_or_404(CarrelloItem, id=item_id)
    item.delete()
    return redirect('carrello')


#-------checkout-------------------------------------------------------------------------------



from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from datetime import timedelta
from .models import Carrello, CarrelloItem, CodiceSconto, Ordine

def checkout(request):
    sessione = request.session.session_key or request.session.create()
    carrello = Carrello.objects.filter(sessione=sessione).first()
    if not carrello:
        carrello = Carrello.objects.create(sessione=sessione)

    items = CarrelloItem.objects.filter(carrello=carrello)

    if not items.exists():
        messages.error(request, "Il tuo carrello è vuoto. L'ordine non può essere processato.")
        return redirect('carrello')

    initial_data = {}
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        profilo = request.user.userprofile
        initial_data = {
            'nome': profilo.nome,
            'cognome': profilo.cognome,
            'indirizzo': profilo.indirizzo,
            'civico': profilo.civico,
            'cap': profilo.cap,
            'citta': profilo.citta,
            'provincia': profilo.provincia,
            'email': request.user.email,
            'telefono': profilo.telefono,
            'codice_fiscale': profilo.codice_fiscale,
        }

    if request.method == 'POST':
        items = CarrelloItem.objects.filter(carrello=carrello)
        if not items.exists():
            messages.error(request, "Il tuo carrello è vuoto. L'ordine non è stato registrato.")
            return redirect('carrello')

        codice_sconto_input = request.POST.get('codice_sconto')
        codice_sconto = None
        if codice_sconto_input:
            codice_sconto = CodiceSconto.objects.filter(codice=codice_sconto_input).first()
            if codice_sconto and codice_sconto.valido_per_utente(request.user):
                carrello.codice_sconto = codice_sconto
                carrello.save()

        fatturazione_diversa = request.POST.get('fatturazioneDiversa') == 'on'

        nome = request.POST.get('nome_spedizione') if fatturazione_diversa else request.POST.get('nome')
        cognome = request.POST.get('cognome_spedizione') if fatturazione_diversa else request.POST.get('cognome')
        indirizzo = request.POST.get('indirizzo_spedizione') if fatturazione_diversa else request.POST.get('indirizzo')
        civico = request.POST.get('civico_spedizione') if fatturazione_diversa else request.POST.get('civico')
        cap = request.POST.get('cap_spedizione') if fatturazione_diversa else request.POST.get('cap')
        citta = request.POST.get('citta_spedizione') if fatturazione_diversa else request.POST.get('citta')
        provincia = request.POST.get('provincia_spedizione') if fatturazione_diversa else request.POST.get('provincia')

        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        codice_fiscale = request.POST.get('codice_fiscale')

        nome_fatt = request.POST.get('nome') if fatturazione_diversa else None
        cognome_fatt = request.POST.get('cognome') if fatturazione_diversa else None
        indirizzo_fatt = request.POST.get('indirizzo') if fatturazione_diversa else None
        civico_fatt = request.POST.get('civico') if fatturazione_diversa else None
        cap_fatt = request.POST.get('cap') if fatturazione_diversa else None
        citta_fatt = request.POST.get('citta') if fatturazione_diversa else None
        provincia_fatt = request.POST.get('provincia') if fatturazione_diversa else None

        ordine = Ordine.objects.create(
            cliente=request.user if request.user.is_authenticated else None,
            codice_fiscale=codice_fiscale,
            email=email,
            telefono=telefono,
            nome=nome,
            cognome=cognome,
            indirizzo=indirizzo,
            civico=civico,
            cap=cap,
            citta=citta,
            provincia=provincia,
            fatturazione_diversa=fatturazione_diversa,
            nome_fatt=nome_fatt,
            cognome_fatt=cognome_fatt,
            indirizzo_fatt=indirizzo_fatt,
            civico_fatt=civico_fatt,
            cap_fatt=cap_fatt,
            citta_fatt=citta_fatt,
            provincia_fatt=provincia_fatt,
        )

        ordine.codice_ordine = f"ORD-{ordine.pk:05d}"
        ordine.save(update_fields=['codice_ordine'])

        for item in items:
            if item.quantita > item.prodotto.disponibilita:
                messages.error(request, f"Disponibilità insufficiente per {item.prodotto.nome}. Ordine annullato.")
                ordine.delete()
                return redirect('carrello')

            ordine.ordineitem_set.create(
                prodotto=item.prodotto,
                quantita=item.quantita,
                prezzo_unitario=item.prodotto.prezzo_scontato
            )
            item.prodotto.disponibilita -= item.quantita
            item.prodotto.save()

        if carrello.codice_sconto and not carrello.codice_sconto.multiuso:
            carrello.codice_sconto.usato = 1
            carrello.codice_sconto.save()

        items.delete()
        carrello.delete()

        request.session['ordine_id'] = ordine.id
        return redirect('riepilogo_ordine')

    return render(request, 'core/checkout.html', {
        'items': items,
        'initial_data': initial_data,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })



#-------------------------------------------------------------------------------------------------------------



from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta
from decimal import Decimal

from .models import Ordine, OrdineItem, PrezzoSpedizione, CodiceSconto, Carrello, CarrelloItem, ContattiBrand

def riepilogo_ordine(request):
    ordine_id = request.session.get('ordine_id')
    if not ordine_id:
        return redirect('checkout')

    ordine = get_object_or_404(Ordine, id=ordine_id)
    articoli = OrdineItem.objects.filter(ordine=ordine)
    totale_prodotti = sum(item.get_subtotale() for item in articoli)

    # Calcolo spedizione
    spedizione = PrezzoSpedizione.objects.first()
    prezzo_spedizione = spedizione.prezzo if spedizione else Decimal('0.00')
    ordine.prezzo_spedizione = spedizione

    # Calcolo sconto
    codice_attivo = request.session.get('codice_sconto')
    sconto_percentuale = 0
    sconto = Decimal('0.00')

    if codice_attivo:
        try:
            codice = CodiceSconto.objects.get(codice=codice_attivo)
            sconto_percentuale = codice.percentuale
            sconto = (totale_prodotti * sconto_percentuale) / 100

            if not codice.multiuso:
                codice.usato = True
                codice.save()

            ordine.codice_sconto = codice
            ordine.sconto_percentuale = sconto_percentuale
        except CodiceSconto.DoesNotExist:
            pass

        request.session.pop('codice_sconto', None)

    totale_finale = totale_prodotti - sconto + prezzo_spedizione
    ordine.totale_pagare = totale_finale

    # Salva sessione carrello
    sessione = request.session.session_key
    if sessione:
        ordine.carrello_sessione = sessione

    ordine.save()

    # Pulisce carrello
    if sessione:
        try:
            carrello = Carrello.objects.get(sessione=sessione)
            CarrelloItem.objects.filter(carrello=carrello).delete()
            carrello.delete()
        except Carrello.DoesNotExist:
            pass

    # Invia email se non ancora inviata e ordine recente
    if not ordine.email_inviata and ordine.email and (now() - ordine.data_creazione) < timedelta(minutes=5):
        contatti = ContattiBrand.objects.first()
        email_admin = contatti.email if contatti and contatti.email else settings.DEFAULT_FROM_EMAIL

        context = {
            'ordine': ordine,
            'contatti': contatti,
            'articoli': articoli
        }

        # Email all'amministratore
        try:
            subject_admin = f"Nuovo ordine ricevuto - Ordine {ordine.codice_ordine}"
            html_admin = render_to_string('email/admin_notifica_ordine.html', context)
            msg_admin = EmailMultiAlternatives(
                subject_admin,
                f"Nuovo ordine {ordine.codice_ordine}",
                settings.DEFAULT_FROM_EMAIL,
                [email_admin]
            )
            msg_admin.attach_alternative(html_admin, "text/html")
            msg_admin.send()
        except Exception as e:
            print(f"Errore invio email all'amministratore: {e}")

        # Email al cliente
        try:
            subject_cliente = f"{contatti.nome if contatti else 'Il tuo negozio'} - Conferma Ordine {ordine.codice_ordine}"
            testo_cliente = f"Gentile {ordine.nome},\nGrazie per il tuo ordine {ordine.codice_ordine}."
            html_cliente = render_to_string('email/conferma_ordine.html', context)

            msg_cliente = EmailMultiAlternatives(
                subject_cliente,
                testo_cliente,
                settings.DEFAULT_FROM_EMAIL,
                [ordine.email]
            )
            msg_cliente.attach_alternative(html_cliente, "text/html")
            msg_cliente.send()
        except Exception as e:
            print(f"Errore invio email al cliente: {e}")

        ordine.email_inviata = True
        ordine.save(update_fields=["email_inviata"])

    # Render pagina riepilogo
    return render(request, 'core/riepilogo_ordine.html', {
        'ordine': ordine,
        'articoli': articoli,
        'totale_prodotti': totale_prodotti,
        'prezzo_spedizione': prezzo_spedizione,
        'sconto': sconto,
        'sconto_percentuale': sconto_percentuale,
        'codice_attivo': codice_attivo,
        'totale_finale': totale_finale,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })




# Metodo per ottenere totale da usare in modelli o admin
def get_totale(self):
    return sum(item.prodotto.prezzo * item.quantita for item in self.ordineitem_set.all())



#----------stripe----------------------------------------------------------------------------------------------------------

stripe.api_key = settings.STRIPE_SECRET_KEY


from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from decimal import Decimal
from django.conf import settings
import stripe

from .models import Ordine, PrezzoSpedizione, CodiceSconto
from amministratore.models import PaymentSettings


def stripe_checkout(request):
    ordine_id = request.session.get('ordine_id')
    if not ordine_id:
        messages.error(request, "Ordine non trovato.")
        return redirect('checkout')

    ordine = get_object_or_404(Ordine, pk=ordine_id)

    # Usa totale_pagare già calcolato in riepilogo_ordine
    totale_pagare = ordine.totale_pagare or Decimal('0.00')

    # Estrai il valore numerico dal modello PrezzoSpedizione
    prezzo_sped = ordine.prezzo_spedizione.prezzo if ordine.prezzo_spedizione else Decimal('0.00')

    # Verifica configurazione Stripe
    settings_pagamento = PaymentSettings.objects.first()
    if not settings_pagamento or not settings_pagamento.stripe_secret_key:
        messages.error(request, "Stripe non configurato.")
        return redirect('gestione_pagamenti')

    stripe.api_key = settings_pagamento.stripe_secret_key

    try:
        # Calcoli per Stripe in centesimi
        prodotti_cent = int((totale_pagare - prezzo_sped) * 100)
        spedizione_cent = int(prezzo_sped * 100)

        line_items = [
            {
                'price_data': {
                    'currency': 'eur',
                    'product_data': {'name': f'Ordine #{ordine.codice_ordine}'},
                    'unit_amount': prodotti_cent,
                },
                'quantity': 1,
            }
        ]

        if spedizione_cent > 0:
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {'name': 'Spese di spedizione'},
                    'unit_amount': spedizione_cent,
                },
                'quantity': 1,
            })

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('successo')),
            cancel_url=request.build_absolute_uri(reverse('annulla_pagamento')),
            customer_email=ordine.email,
        )

        return redirect(session.url, code=303)

    except stripe.error.StripeError as e:
        messages.error(request, f"Errore Stripe: {str(e)}")
        return redirect('checkout')


def annulla_pagamento(request):
    ordine_id = request.session.get('ordine_id')
    if not ordine_id:
        return redirect('home')

    ordine = get_object_or_404(Ordine, id=ordine_id)

    if not ordine.pagato:
        codice = ordine.codice_ordine
        email_cliente = ordine.email

        # Ripristina disponibilità dei prodotti
        for item in ordine.ordineitem_set.all():
            prodotto = item.prodotto
            prodotto.disponibilita += item.quantita
            prodotto.save()

        ordine.delete()

        if 'ordine_id' in request.session:
            del request.session['ordine_id']

        # Email all’amministratore
        oggetto = f"Ordine {codice} annullato dall'utente"
        corpo = f"L'utente ha annullato l'ordine {codice} tornando indietro da Stripe."
        email_admin = settings.DEFAULT_FROM_EMAIL
        try:
            EmailMessage(oggetto, corpo, to=[email_admin]).send()
        except Exception as e:
            print(f"Errore invio email admin: {e}")

        messages.warning(request, f"L'ordine {codice} è stato annullato.")

    return redirect('home')












#--------------------------------------------------------------------------------------------------
from core.models import Ordine, Carrello, CarrelloItem

def successo(request):
    sessione = request.session.session_key
    ordine_id = request.session.get('ordine_id')

    if not ordine_id:
        return redirect('home')

    ordine = get_object_or_404(Ordine, id=ordine_id)
    articoli = ordine.ordineitem_set.select_related('prodotto').all()

    # Salva come pagato
    ordine.pagato = True
    ordine.save()

    # Cancella carrello
    if sessione:
        try:
            carrello = Carrello.objects.get(sessione=sessione)
            CarrelloItem.objects.filter(carrello=carrello).delete()
            carrello.delete()
        except Carrello.DoesNotExist:
            pass

    # Pulisce la sessione
    if 'ordine_id' in request.session:
        del request.session['ordine_id']

    return render(request, 'core/successo.html', {
        'ordine': ordine,
        'articoli': articoli
    })


#----------------altro--------------------------------------------------------------------------------------------
from django.shortcuts import render, get_object_or_404
from core.models import Ordine

def ordine_completato(request):
    ordine_id = request.session.get('ordine_id')
    if not ordine_id:
        return redirect('home')

    ordine = get_object_or_404(Ordine, id=ordine_id)

    return render(request, 'core/ordine_completato.html', {
        'ordine': ordine
    })


#-+--------------------------------------------------------------------------------------------------------

def wishlist(request):
    return render(request, 'core/wishlist.html')

#------contatti-------------------------------------------------------------------------------------------------------------

def contatti_view(request):
    if request.method == 'POST':
        email = request.POST.get('email') or (request.user.email if request.user.is_authenticated else None)
        oggetto = request.POST.get('oggetto')
        messaggio = request.POST.get('messaggio')

        if email and oggetto and messaggio:
            MessaggioContatto.objects.create(
                email=email,
                oggetto=oggetto,
                messaggio=messaggio
            )
            messages.success(request, "Il tuo messaggio è stato inviato correttamente.")
            return redirect('contatti')  # o la pagina che vuoi
        else:
            messages.error(request, "Tutti i campi sono obbligatori.")
    
    return render(request, 'core/contatti.html')


def contatti(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        oggetto = request.POST.get('oggetto')
        messaggio = request.POST.get('messaggio')
        allegato = request.FILES.get('allegato')

        m = MessaggioContatto(email=email, oggetto=oggetto, messaggio=messaggio)
        if allegato:
            m.allegato = allegato
        m.save()

        return HttpResponseRedirect(reverse('contatti') + '?success=1')

    return render(request, 'core/contatti.html')


#-------ordini---------------------------------------------------------------------------


def ordini(request):
    ordini = Ordine.objects.filter(cliente=request.user)
    return render(request, 'core/ordini.html', {
        'ordini': ordini
    })

#---------editor------------------------------------------------------------------------------------------


@staff_member_required
def editor_visuale(request):
    return render(request, 'editor.html')


def editor_home(request):
    elementi = HomeElemento.objects.all().order_by('zona', 'ordine')

    # Raggruppamento per zona (in Python, non nel template)
    elementi_per_zona = defaultdict(list)
    for el in elementi:
        elementi_per_zona[el.zona].append(el)

    return render(request, 'core/editor_home.html', {
        'elementi_per_zona': dict(elementi_per_zona),
    })


@csrf_exempt
def salva_layout(request):
    if request.method == 'POST':
        dati = json.loads(request.body)
        layout, created = LayoutSalvato.objects.get_or_create(nome="Home Layout")
        layout.dati_json = json.dumps(dati)
        layout.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)



def check_session(request):
    return JsonResponse({'status': 'active'})

#----pagina dinamica------------------------------------------------------------------------------

def pagina_dinamica(request, slug):
    pagina = get_object_or_404(PaginaInformativa, slug=slug)
    return render(request, 'core/pagina_dinamica.html', {'pagina': pagina})

#---------ricerca-------------------------------------------------------------------------------------------

import re

def evidenzia(query, testo):
    """
    Evidenzia la query nel testo, senza distinguere tra maiuscole e minuscole,
    preservando il caso originale del testo.
    """
    if not query:
        return testo
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", testo)


def ricerca_view(request):
    query = request.GET.get('q', '').strip()
    risultati = []
    pagine_trovate = []
    contenuti_mongo = []

    if query:
        query_lower = query.lower()

        # 1. Ricerca nei modelli SQL
        prodotti = Prodotto.objects.filter(
            Q(nome__icontains=query) | Q(descrizione__icontains=query) | Q(colorazioni__icontains=query)
        )
        categorie = Categoria.objects.filter(
            Q(nome__icontains=query) | Q(descrizione__icontains=query)
        )
        sottocategorie = SottoCategoria.objects.filter(
            Q(nome__icontains=query) | Q(descrizione__icontains=query)
        )
        informative = Informativa.objects.filter(
            Q(titolo__icontains=query) | Q(contenuto__icontains=query)
        )

        # 2. Ricerca nei contenuti MongoDB
        contenuti_mongo_queryset = Contenuto.objects.filter(
            MQ(titolo__icontains=query) | MQ(contenuto__icontains=query) | MQ(url_pagina__icontains=query)
        )

        for contenuto in contenuti_mongo_queryset:
            contenuti_mongo.append({
                'titolo': contenuto.titolo,
                'url': contenuto.url_pagina,
                'snippet': evidenzia(query, contenuto.contenuto[:300])
            })

        # 3. Ricerca nelle pagine statiche
        pagine_statiche = [
            ("Chi siamo", "core/chi_siamo.html"),
            ("Sostenibilità", "core/sostenibilita.html"),
            ("FAQ", "core/faq.html"),
            ("Spedizione", "core/spedizione.html"),
            ("Resi", "core/resi.html"),
            ("Termini e Condizioni", "core/termini_condizioni.html"),
            ("Trattamento Dati", "core/trattamento_dati.html"),
            ("Informativa Privacy", "core/informativa_privacy.html"),
            ("Pagamenti", "core/pagamenti.html"),
            ("Cookie", "core/cookie.html"),
        ]

        for titolo, template_path in pagine_statiche:
            full_path = os.path.join(settings.BASE_DIR, "templates", template_path)
            if os.path.exists(full_path):
                with open(full_path, encoding='utf-8') as f:
                    contenuto = f.read().lower()
                    if query_lower in contenuto or SequenceMatcher(None, query_lower, contenuto).ratio() > 0.45:
                        inizio = contenuto.find(query_lower)
                        snippet = contenuto[max(0, inizio - 40):inizio + 160] if inizio != -1 else contenuto[:200]
                        snippet_html = evidenzia(query, snippet)
                        pagine_trovate.append({
                            "titolo": titolo,
                            "url": reverse(template_path.split('/')[-1].replace('.html', '')),
                            "snippet": snippet_html
                        })

        risultati = list(prodotti) + list(categorie) + list(sottocategorie) + list(informative)

    return render(request, 'core/risultati_ricerca.html', {
        'query': query,
        'risultati': risultati,
        'contenuti_mongo': contenuti_mongo,
        'pagine_trovate': pagine_trovate,
    })







#----------------------------------------------------------------------------------------------------------------------



@csrf_exempt
def salva_cookie_consent(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            scelta = data.get('consent', 'nessuna')
            ip = request.META.get('REMOTE_ADDR')

            # Se l'utente è autenticato, collega anche l'user
            CookieConsent.objects.create(
                user=request.user if request.user.is_authenticated else None,
                ip_address=ip,
                scelta=scelta
            )

            request.session['cookie_consent'] = scelta
            return JsonResponse({'status': 'ok', 'message': 'Consenso salvato'})
        except Exception as e:
            return JsonResponse({'status': 'errore', 'message': str(e)}, status=400)

    return JsonResponse({'error': 'Metodo non consentito'}, status=405)


#--------------------------------------------------------------------------------------------------------

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone
from .forms import CodiceScontoForm
from .models import CodiceSconto

@login_required
def applica_sconto_view(request):
    totale = Decimal('100.00')  # Sostituiscilo con il totale reale del carrello
    scontato = totale

    if request.method == 'POST':
        form = CodiceScontoForm(request.POST)
        if form.is_valid():
            codice_input = form.cleaned_data['codice'].strip()
            try:
                codice_sconto = CodiceSconto.objects.get(codice=codice_input)

                # Verifica che lo sconto sia legato all'utente attuale
                if codice_sconto.utente != request.user:
                    messages.error(request, "❌ Questo codice sconto non è associato al tuo account.")
                    return render(request, 'carrello/applica_sconto.html', {
                        'form': form, 'totale': totale, 'scontato': scontato
                    })

                # Controlla se è valido (attivo, non usato, non scaduto)
                if not codice_sconto.attivo or codice_sconto.usato:
                    messages.error(request, "❌ Codice sconto non valido o già usato.")
                elif codice_sconto.scadenza and codice_sconto.scadenza < timezone.now().date():
                    messages.error(request, "❌ Codice sconto scaduto.")
                else:
                    # Applica lo sconto
                    scontato = codice_sconto.applica_sconto(totale)
                    codice_sconto.usato = True
                    codice_sconto.save()

                    # Se non è multiuso → elimina
                    if not codice_sconto.multiuso:
                        codice_sconto.delete()

                    messages.success(request, f"✅ Sconto applicato! Nuovo totale: €{scontato:.2f}")

            except CodiceSconto.DoesNotExist:
                messages.error(request, "❌ Codice sconto non valido.")
    else:
        form = CodiceScontoForm()

    return render(request, 'carrello/applica_sconto.html', {
        'form': form,
        'totale': totale,
        'scontato': scontato
    })




def scelta_pagamento(request):
    if request.method == 'POST':
        metodo = request.POST.get('metodo_pagamento')

        if metodo == 'stripe':
            return redirect('stripe_checkout')
        elif metodo == 'paypal':
            return redirect('paypal_checkout')
        elif metodo == 'scalapay':
            return redirect('scalapay_checkout')
        else:
            return redirect('riepilogo_ordine')  # Se non seleziona nulla, torna

    return redirect('riepilogo_ordine')


#-----------------------------------------------------------------------------------------------------------


# PayPal - redirect simulato
def paga_con_paypal(request, ordine_id):
    ordine = get_object_or_404(Ordine, pk=ordine_id)
    return redirect('successo')  # simulazione, da integrare se vuoi con API PayPal reali





def paypal_payment(request):
    if request.method == 'POST':
        settings_pagamento = PaymentSettings.objects.first()

        if not settings_pagamento or not settings_pagamento.paypal_client_id:
            return redirect('gestione_pagamenti')

        context = {
            'paypal_url': 'https://www.sandbox.paypal.com/cgi-bin/webscr' if settings_pagamento.paypal_mode == 'sandbox' else 'https://www.paypal.com/cgi-bin/webscr',
            'business_email': settings_pagamento.paypal_client_id,  # deve essere l’email business
            'amount': '10.00',  # oppure il totale ordine dinamico
            'currency_code': 'EUR',
            'return_url': 'http://127.0.0.1:8000/pagamento-completato/',
            'cancel_url': 'http://127.0.0.1:8000/pagamento-annullato/',
        }

        return render(request, 'core/paypal_payment.html', context)

    return redirect('dashboard')







def paypal_checkout(request):
    ordine_id = request.session.get('ordine_id')
    if not ordine_id:
        return redirect('checkout')

    ordine = get_object_or_404(Ordine, id=ordine_id)

    # Recupera le chiavi PayPal dal DB
    settings_pagamento = PaymentSettings.objects.first()
    if not settings_pagamento or not settings_pagamento.paypal_client_id or not settings_pagamento.paypal_secret_key:
        return redirect('gestione_pagamenti')

    # Configura PayPal SDK con i dati del DB
    paypalrestsdk.configure({
        "mode": settings_pagamento.paypal_mode,  # 'sandbox' o 'live'
        "client_id": settings_pagamento.paypal_client_id,
        "client_secret": settings_pagamento.paypal_secret_key
    })

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('paypal_success')),
            "cancel_url": request.build_absolute_uri(reverse('checkout'))
        },
        "transactions": [{
            "amount": {
                "total": str(ordine.get_totale()),
                "currency": "EUR"
            },
            "description": f"Pagamento Ordine #{ordine.id}"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(str(link.href))
    else:
        print("Errore PayPal:", payment.error)
        return redirect('riepilogo_ordine')
    



def paypal_success(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    settings_pagamento = PaymentSettings.objects.first()
    paypalrestsdk.configure({
        "mode": settings_pagamento.paypal_mode,
        "client_id": settings_pagamento.paypal_client_id,
        "client_secret": settings_pagamento.paypal_secret_key
    })

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        messages.success(request, "✅ Pagamento completato con successo!")
        return render(request, 'core/paypal_success.html')
    else:
        messages.error(request, "❌ Errore nel completamento del pagamento.")
        return redirect('checkout')


#-----------------------------------------------------------------------------------------------------

# Scalapay - redirect simulato
def paga_con_scalapay(request, ordine_id):
    ordine = get_object_or_404(Ordine, pk=ordine_id)
    return redirect('successo')  # simulazione, da sostituire con API Scalapay

#----------------------------------------------------------------------------------------------------------------

import requests

def scalapay_checkout(request):
    ordine_id = request.session.get('ordine_id')
    if not ordine_id:
        return redirect('checkout')

    ordine = get_object_or_404(Ordine, id=ordine_id)

    url = 'https://staging.api.scalapay.com/v2/orders' if settings.SCALAPAY_SANDBOX else 'https://api.scalapay.com/v2/orders'
    headers = {
        'Authorization': f'Bearer {settings.SCALAPAY_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        "totalAmount": {
            "amount": str(ordine.get_totale()),
            "currency": "EUR"
        },
        "consumer": {
            "email": ordine.email
        },
        "merchantReference": str(ordine.id),
        "merchant": {
            "redirectConfirmUrl": request.build_absolute_uri(reverse('successo')),
            "redirectCancelUrl": request.build_absolute_uri(reverse('checkout'))
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        checkout_url = response.json().get('checkoutUrl')
        return redirect(checkout_url)
    else:
        print(response.text)
        return redirect('riepilogo_ordine')

#--------------------------------------------------------------------------------------------------------------
# ===========================
# DASHBOARD PRINCIPALE ADMIN
# ===========================
def dashboard(request):
    return render(request, 'amministratore/dashboard.html')

# ===========================--------------------------------------------------------------------------
# DASHBOARD RACCOLTA DATI
# ===========================
#def dati_home(request):
 #   contenuti = ContentText.objects()
  #  richieste = UserRequest.objects()
   # log_entries = LogEntry.objects()

    #return render(request, 'amministratore/dati_home.html', {
     #   'contenuti': contenuti,
      #  'richieste': richieste,
       # 'log_entries': log_entries,
    #})

# ===========================---------------------------------------------------------------------------
# DASHBOARD GLOBALE
# ===========================
#def dashboard_globale(request):
 #   contenuti = ContentText.objects()
  #  richieste = UserRequest.objects()
   # log_entries = LogEntry.objects()
    #pagine = []  # Se hai un modello Pagina usa: Pagina.objects.all()
#
 #   return render(request, 'amministratore/dashboard_globale.html', {
  #      'contenuti': contenuti,
   #     'richieste': richieste,
    #    'log_entries': log_entries,
     #   'pagine': pagine,
    #})

# ===========================------------------------------------------------------------------------
# LISTE SINGOLE
# ===========================
def contenuti_lista(request):
    contenuti = ContentText.objects()
    return render(request, 'amministratore/contenuti_lista.html', {'contenuti': contenuti})

def richieste_lista(request):
    richieste = UserRequest.objects()
    return render(request, 'amministratore/richieste_lista.html', {'richieste': richieste})

def log_lista(request):
    log_entries = LogEntry.objects()
    return render(request, 'amministratore/log_lista.html', {'log_entries': log_entries})

# ===========================----------------------------------------------------------------------------
# SALVA CONTENUTO IN MONGODB
# ===========================
def salva_contenuto_view(request):
    if request.method == 'POST':
        titolo = request.POST.get('titolo')
        contenuto = request.POST.get('contenuto')
        url = request.POST.get('url')

        salva_contenuto(titolo, contenuto, url)

        return redirect('dashboard-contenuti')
#----------------------------------------------------------------------------------------------

# core/views.py (aggiungi alla fine)



def categorie_list(request):
    categorie = Categoria.objects.all()
    return render(request, 'amministratore/categorie_list.html', {'categorie': categorie})


@login_required
def dati_home(request):
    contenuti = Contenuto.objects.all()
    richieste = Richiesta.objects.all()
    log_entries = LogEvento.objects.all()

    context = {
        'contenuti': contenuti,
        'richieste': richieste,
        'log_entries': log_entries,
    }
    return render(request, 'amministratore/dati_home.html', context)

#--------------------------------------------------------------------------------------------------------

@login_required
def dashboard_globale(request):
    contenuti = Contenuto.objects.all()
    richieste = Richiesta.objects.all()
    log_entries = LogEvento.objects.all()

    context = {
        'contenuti': contenuti,
        'richieste': richieste,
        'log_entries': log_entries,
    }
    return render(request, 'amministratore/dashboard_globale.html', context)

#---------------------------------------------------------------------------------------------------------

@login_required
def dati_home(request):
    contenuti = Contenuto.objects.all()
    richieste = Richiesta.objects.all()
    log_entries = LogEvento.objects.all()

    context = {
        'contenuti': contenuti,
        'richieste': richieste,
        'log_entries': log_entries,
    }
    return render(request, 'amministratore/dati_home.html', context)
#-----------------------------------------------------------------------------------------------------------

@login_required
def dashboard_globale(request):
    contenuti = Contenuto.objects.all()
    richieste = Richiesta.objects.all()
    log_entries = LogEvento.objects.all()

    context = {
        'contenuti': contenuti,
        'richieste': richieste,
        'log_entries': log_entries,
    }
    return render(request, 'amministratore/dashboard_globale.html', context)

#---------------------------------------------------------------------------------------------------------

from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from datetime import date
from django.db.models import Q
from .models import CodiceSconto

@staff_member_required
def elimina_codici_scaduti_admin(request):
    oggi = date.today()

    codici_da_eliminare = CodiceSconto.objects.filter(
        Q(usato=True, multiuso=False) | Q(scadenza__lt=oggi)
    )

    count = codici_da_eliminare.count()
    codici_da_eliminare.delete()

    messages.success(request, f"{count} codice/i sconto eliminati.")
    return redirect('/admin/')





#-----------------------------------------------------------------------------------------------------------
