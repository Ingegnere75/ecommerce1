import random
import re
import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate, login, logout, update_session_auth_hash
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from xhtml2pdf import pisa
from .forms import ModificaProfiloForm, ReclamoForm
from .models import UserProfile, Reclamo, Wishlist, Cookie
from core.models import Ordine, Carrello, CarrelloItem, Prodotto
from core.services.log_manager import registra_evento  # 🔥 il nostro logger MongoDB
from datetime import timezone


# ===========================----------------------------------------------------------------------
# DASHBOARD UTENTE
# ===========================
@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

# ===========================-------------------------------------------------------------------------
# LOGIN
# ===========================
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            registra_evento(request, 'Login', 'Utente loggato')

            if user.is_staff or user.is_superuser:
                return redirect('admin-dashboard')  # Dashboard amministratore
            else:
                return redirect('dashboard')  # Dashboard utente normale
        else:
            return render(request, 'accounts/login.html', {'error': 'Credenziali non valide'})

    return render(request, 'accounts/login.html')

# ===========================---------------------------------------------------------------------------
# LOGOUT
# ===========================
def logout_view(request):
    if request.user.is_authenticated:
        registra_evento(request, 'Logout', 'Utente disconnesso')
    logout(request)
    return redirect('login')

# ===========================-------------------------------------------------------------------------------
# REGISTRAZIONE
# ===========================

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        nome = request.POST.get('nome')
        cognome = request.POST.get('cognome')
        indirizzo = request.POST.get('indirizzo')
        civico = request.POST.get('civico')
        cap = request.POST.get('cap')
        citta = request.POST.get('citta')
        provincia = request.POST.get('provincia')
        codice_fiscale = request.POST.get('codice_fiscale')
        telefono = request.POST.get('telefono')
#----------------------------------------------------------------------------------------------------------
        # Verifica se l'email è già registrata
        if User.objects.filter(email=email).exists():
            messages.error(request, "❌ Email già registrata.")
            return render(request, 'accounts/register.html')
#---------------------------------------------------------------------------------------------------------
        # Verifica robustezza password
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[\d\W]', password):
            messages.error(request, "❗ La password deve contenere almeno 8 caratteri, una maiuscola, una minuscola, un numero o simbolo.")
            return render(request, 'accounts/register.html')
#---------------------------------------------------------------------------------------------------------
        # Verifica corrispondenza password
        if password != password2:
            messages.error(request, "❗ Le password non coincidono.")
            return render(request, 'accounts/register.html')
#--------------------------------------------------------------------------------------------------------------------
        # Genera OTP e salva dati in sessione
        otp = str(random.randint(100000, 999999))
        request.session['registration_data'] = {
            'email': email,
            'password': password,
            'nome': nome,
            'cognome': cognome,
            'indirizzo': indirizzo,
            'civico': civico,
            'cap': cap,
            'citta': citta,
            'provincia': provincia,
            'codice_fiscale': codice_fiscale,
            'telefono': telefono,
            'otp': otp,
        }
#------------------------------------------------------------------------------------------------------------------
        # Invia email con OTP
        try:
            send_mail(
                'Il tuo codice OTP - Verifica email',
                f'Ciao {nome},\n\nEcco il tuo codice OTP per completare la registrazione: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            messages.error(request, f"Errore durante l'invio dell'email: {e}")
            return render(request, 'accounts/register.html')

        messages.info(request, f"📧 È stato inviato un codice OTP a {email}.")
        return redirect('confirm_otp')

    return render(request, 'accounts/register.html')
#-----------------------------------------------------------------------------------------------------------------

def confirm_otp(request):
    data = request.session.get('registration_data')

    if not data:
        messages.error(request, "⚠️ Sessione scaduta. Riprova la registrazione.")
        return redirect('register')

    # Inizializza i tentativi se non presenti
    if 'otp_attempts' not in request.session:
        request.session['otp_attempts'] = 0

    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        session_otp = data.get('otp')

        if user_otp != session_otp:
            request.session['otp_attempts'] += 1

            if request.session['otp_attempts'] >= 2:
                del request.session['registration_data']
                del request.session['otp_attempts']
                messages.error(request, "❌ Troppi tentativi. Ritorno alla home.")
                return redirect('home')

            messages.error(request, "❌ Codice OTP errato. Riprova.")
            return render(request, 'accounts/confirm_otp.html')

        # ✅ OTP corretto → Crea utente
        user = User.objects.create_user(username=data['email'], email=data['email'], password=data['password'])
        UserProfile.objects.create(
            user=user,
            nome=data['nome'],
            cognome=data['cognome'],
            indirizzo=data['indirizzo'],
            civico=data['civico'],
            cap=data['cap'],
            citta=data['citta'],
            provincia=data['provincia'],
            codice_fiscale=data['codice_fiscale'],
            telefono=data['telefono']
        )
#------------------------------------------------------------------------------------------------------------------
        # ✅ Pulisce sessione
        del request.session['registration_data']
        request.session.pop('otp_attempts', None)

        messages.success(request, "✅ Registrazione completata con successo. Ora effettua il login.")
        return redirect('login')

    return render(request, 'accounts/confirm_otp.html')

# ===========================---------------------------------------------------------------------------------------
# DASHBOARD
# ===========================


# ===========================-------------------------------------------------------------------------------------
# PROFILO
# ===========================
@login_required
def profilo(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)

    if request.method == 'POST':
        form = ModificaProfiloForm(request.POST, instance=profile, user=user)
        if form.is_valid():
            form.save()
            registra_evento(request, 'Profilo', 'Modifica profilo utente')
            messages.success(request, "✅ Profilo aggiornato con successo!")
            return redirect('profilo')
    else:
        form = ModificaProfiloForm(instance=profile, user=user)

    return render(request, 'accounts/profilo.html', {'form': form})

# ===========================-----------------------------------------------------------------------------------
# ORDINI
# ===========================
@login_required
def ordini(request):
    return render(request, 'accounts/ordini.html')

# ===========================-----------------------------------------------------------------------------------
# RECLAMI
# ===========================
@login_required
def reclami(request):
    return render(request, 'accounts/reclami.html')

# ===========================---------------------------------------------------------------------------------
# TICKET
# ===========================
@login_required
def ticket(request):
    return render(request, 'accounts/ticket.html')

# ===========================--------------------------------------------------------------------------------
# LOGOUT CUSTOM
# ===========================
def logout_view(request):
    if request.user.is_authenticated:
        registra_evento(request, 'Logout', 'Utente disconnesso (home)')
    logout(request)
    return redirect('home')

def custom_logout(request):
    if request.user.is_authenticated:
        registra_evento(request, 'Logout', 'Logout con flush sessione')
    logout(request)
    request.session.flush()
    return redirect('/')

# ===========================---------------------------------------------------------------------------------
# VERIFICA OTP
# ===========================
def verifica_otp(request):
    if request.method == 'POST':
        codice = request.POST.get('otp')
        if codice == request.session.get('otp'):
            user_id = request.session.get('user_id')
            user = User.objects.get(id=user_id)
            login(request, user)

            registra_evento(request, 'Login', 'Login con OTP')

            del request.session['otp']
            del request.session['user_id']

            return redirect('admin-dashboard')
        else:
            return render(request, 'accounts/verifica_otp.html', {'errore': 'Codice errato'})

    return render(request, 'accounts/verifica_otp.html')

# ===========================--------------------------------------------------------------------------------------
# INVIA RECLAMO
# ===========================
def genera_numero_ordine():
    while True:
        numero = f"ORD-{random.randint(100000, 999999)}"
        if not Reclamo.objects.filter(numero_ordine=numero).exists():
            return numero

@login_required
def invia_reclamo(request):
    if request.method == 'POST':
        form = ReclamoForm(request.POST, request.FILES)
        if form.is_valid():
            reclamo = form.save(commit=False)
            reclamo.utente = request.user
            reclamo.numero_ordine = genera_numero_ordine()
            reclamo.stato = 'aperto'
            reclamo.esito = ''
            reclamo.save()

            registra_evento(request, 'Reclamo', 'Inviato nuovo reclamo', {'numero_ticket': reclamo.numero_ticket})

            subject = f"Nuovo Reclamo - Ticket #{reclamo.numero_ticket}"
            message = (
                f"Nome: {reclamo.nome} {reclamo.cognome}\n"
                f"Email: {reclamo.email}\n"
                f"Numero Ordine: {reclamo.numero_ordine}\n"
                f"Oggetto: {reclamo.oggetto}\n"
                f"Messaggio:\n{reclamo.messaggio}\n"
                f"Numero Ticket: {reclamo.numero_ticket}"
            )

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMINS[0][1]],
                fail_silently=False,
            )

            request.session['ticket_id'] = reclamo.id
            return redirect('ticket')
    else:
        form = ReclamoForm()

    return render(request, 'accounts/reclami.html', {'form': form})


# ===========================---------------------------------------------------------------------------------
# VISUALIZZA TICKET
# ===========================
@login_required
def ticket_view(request):
    ticket_id = request.session.get('ticket_id')
    if not ticket_id:
        return redirect('home')

    try:
        ticket = Reclamo.objects.get(id=ticket_id, utente=request.user)
    except Reclamo.DoesNotExist:
        return redirect('home')

    del request.session['ticket_id']

    return render(request, 'accounts/ticket.html', {'ticket': ticket})



def lista_reclami(request):
    reclami = Reclamo.objects.filter(utente=request.user).order_by('-data_invio')
    return render(request, 'accounts/lista_reclami.html', {'reclami': reclami})


# ===========================--------------------------------------------------------------------------------------
# CONSULTA RECLAMI
# ===========================
@login_required
def consulta_reclami(request):
    reclami = Reclamo.objects.filter(utente=request.user).order_by('-data_invio')
    return render(request, 'accounts/consulta_reclami.html', {'reclami': reclami})

# ===========================-------------------------------------------------------------------------------------
# RESET PASSWORD (CON LOGOUT)
# ===========================


def generate_otp():
    return str(random.randint(100000, 999999))
#-----------------------------------------------------------------------------------------------------------------
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email non trovata.")
            return redirect('password_reset_request')

        otp = generate_otp()
        request.session['reset_email'] = email
        request.session['reset_otp'] = otp

        send_mail(
            'Codice di Verifica per il Reset Password',
            f'Il tuo codice OTP è: {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        messages.success(request, "✅ Codice inviato alla tua email.")
        return redirect('password_reset_verify')

    return render(request, 'accounts/password_reset_request.html')
#------------------------------------------------------------------------------------------------------------------
def password_reset_verify(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        otp_session = request.session.get('reset_otp')

        if otp_input == otp_session:
            messages.success(request, "✅ Codice corretto. Ora puoi reimpostare la password.")
            return redirect('password_reset_new_password')
        else:
            messages.error(request, "❌ Codice errato. Riprova.")
            return redirect('password_reset_verify')

    return render(request, 'accounts/password_reset_verify.html')
#-------------------------------------------------------------------------------------------------------------------
def password_reset_new_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, "❌ Le password non coincidono.")
            return redirect('password_reset_new_password')

        if len(password) < 8:
            messages.error(request, "❌ La password deve contenere almeno 8 caratteri.")
            return redirect('password_reset_new_password')

        email = request.session.get('reset_email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Errore, utente non trovato.")
            return redirect('password_reset_request')

        user.set_password(password)
        user.save()

        # Puliamo la sessione
        del request.session['reset_email']
        del request.session['reset_otp']

        messages.success(request, "✅ Password aggiornata! Ora puoi accedere.")
        return redirect('login')

    return render(request, 'accounts/password_reset_new_password.html')

# VISUALIZZA ORDINI UTENTE
# ===========================--------------------------------------------------------------------------------------
@login_required
def miei_ordini(request):
    ordini = Ordine.objects.filter(cliente=request.user).order_by('-data_creazione')
    return render(request, 'accounts/miei_ordini.html', {'ordini': ordini})

# ===========================------------------------------------------------------------------------------------
# ESPORTA ORDINE PDF
# ===========================
def esporta_ordine_pdf(request, ordine_id):
    ordine = Ordine.objects.get(pk=ordine_id)
    profilo = UserProfile.objects.filter(user=ordine.cliente).first()

    template_path = 'pdf/fattura_ordine.html'
    context = {'ordine': ordine, 'profilo': profilo}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="ordine_{ordine.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Errore nella generazione del PDF', status=500)

    registra_evento(request, 'Ordini', 'Esportato ordine in PDF', {'ordine_id': ordine.id})
    return response

# ===========================---------------------------------------------------------------------------------------
# RIORDINA ORDINE
# ===========================
@login_required
def riordina_ordine(request, ordine_id):
    ordine = get_object_or_404(Ordine, id=ordine_id, cliente=request.user)

    sessione = request.session.session_key
    if not sessione:
        request.session.create()

    carrello, created = Carrello.objects.get_or_create(sessione=sessione)
    carrello.carrelloitem_set.all().delete()

    for item in ordine.ordineitem_set.all():
        CarrelloItem.objects.create(
            carrello=carrello,
            prodotto=item.prodotto,
            quantita=item.quantita
        )

    registra_evento(request, 'Carrello', 'Riordinato un ordine', {'ordine_id': ordine_id})
    return redirect('checkout')

# ===========================-------------------------------------------------------------------------------------
# WISHLIST
# ===========================
@require_POST
@login_required
def toggle_wishlist(request, prodotto_id):
    prodotto = get_object_or_404(Prodotto, id=prodotto_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, prodotto=prodotto)

    if not created:
        wishlist_item.delete()
        added = False
    else:
        added = True

    registra_evento(request, 'Wishlist', 'Modifica wishlist', {'prodotto_id': prodotto_id, 'added': added})
    return JsonResponse({'added': added})
#----------------------------------------------------------------------------------------------------------------------
@login_required
def mia_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('prodotto')
    return render(request, 'accounts/wishlist.html', {'wishlist_items': wishlist_items})
#--------------------------------------------------------------------------------------------------------------------
@login_required
def rimuovi_dalla_wishlist(request, prodotto_id):
    Wishlist.objects.filter(user=request.user, prodotto_id=prodotto_id).delete()
    registra_evento(request, 'Wishlist', 'Prodotto rimosso', {'prodotto_id': prodotto_id})
    return redirect('mia_wishlist')
#--------------------------------------------------------------------------------------------------------------------
@login_required
def aggiungi_dalla_wishlist_al_carrello(request, prodotto_id):
    prodotto = get_object_or_404(Prodotto, id=prodotto_id)

    carrello, _ = Carrello.objects.get_or_create(sessione=request.session.session_key)
    item, created = CarrelloItem.objects.get_or_create(carrello=carrello, prodotto=prodotto)

    if not created:
        item.quantita += 1
        item.save()

    Wishlist.objects.filter(user=request.user, prodotto=prodotto).delete()

    registra_evento(request, 'Carrello', 'Aggiunto prodotto da wishlist', {'prodotto_id': prodotto_id})
    return redirect('mia_wishlist')

# ===========================--------------------------------------------------------------------------------------
# COOKIE CONSENT SALVATAGGIO
# ===========================
@csrf_exempt
def salva_cookie_consent(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        scelta = data.get('consent', 'nessuna')
        request.session['cookie_consent'] = scelta

        registra_evento(request, 'Cookie', 'Cookie consent salvato', {'scelta': scelta})
        return JsonResponse({'status': 'ok', 'message': 'Consenso salvato'})
    
    return JsonResponse({'error': 'Metodo non consentito'}, status=405)
#-------------------------------------------------------------------------------------------------------------------

@login_required
def cookie_user_view(request):
    cookies = Cookie.objects.filter(user=request.user)
    return render(request, 'accounts/cookie_user.html', {'cookies': cookies})
#-----------------------------------------------------------------------------------------------------------------
@login_required
def elimina_cookie_user(request, cookie_id):
    cookie = get_object_or_404(Cookie, id=cookie_id, user=request.user)
    cookie.delete()
    return redirect('cookie_user')
#-------------------------------------------------------------------------------------------------------------------
@login_required
def elimina_tutti_cookie_user(request):
    Cookie.objects.filter(user=request.user).delete()
    return redirect('cookie_user')
#------------------------------------------------------------------------------------------------------------------
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from  core.models import CodiceSconto

@login_required
def lista_sconti(request):
    sconti = CodiceSconto.objects.filter(utente=request.user)
    return render(request, 'accounts/lista_sconti.html', {'sconti': sconti})

#-----------------------------------------------------------------------------------------------------
