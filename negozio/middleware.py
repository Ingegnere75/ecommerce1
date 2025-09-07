from django.shortcuts import redirect
from django.contrib.auth import logout

from django.shortcuts import redirect
from django.contrib.auth import logout

class BloccaAccessoAdminManualeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        referer = request.META.get('HTTP_REFERER', '')

        # Permetti sempre login/register/signup
        if path.endswith('/login/') or path.endswith('/register/') or path.endswith('/signup/'):
            return self.get_response(request)

        # Blocca accesso diretto a /admin/ se non proviene dalla dashboard o non è staff
        if path.startswith('/admin/'):
            if '/amministratore/dashboard/' not in referer and not request.user.is_staff:
                logout(request)
                return redirect('/')

        # Blocca tutto accounts/ tranne login e signup
        if path.startswith('/accounts/') and not any(x in path for x in ['login', 'register', 'signup']):
            if not referer or request.get_host() not in referer:
                logout(request)
                return redirect('/')

        return self.get_response(request)





from django.contrib import auth
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
import datetime

class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        now = datetime.now()

        timeout = 600  # ⏱ 10 minuti

        last_activity = request.session.get('last_activity')

        if last_activity:
            elapsed = (now - datetime.strptime(last_activity, "%Y-%m-%d %H:%M:%S")).total_seconds()
            if elapsed > timeout:
                auth.logout(request)
                return redirect('/')

        # ⏳ Aggiorna il timestamp della sessione
        request.session['last_activity'] = now.strftime("%Y-%m-%d %H:%M:%S")



from django.contrib.auth import logout
from django.shortcuts import redirect

class SessionStrictMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Se l'utente è loggato ma non ha sessione attiva → logout
        if request.user.is_authenticated and not request.session.session_key:
            logout(request)
            return redirect('/')
        return self.get_response(request)




from core.models import InteractionLog  # <-- importa il modello giusto da core
from django.utils.deprecation import MiddlewareMixin

class LogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            InteractionLog.objects.create(
                user=request.user,
                action_type='view',
                model_name='',  # lo lasciamo vuoto oppure puoi aggiungere qualcosa
                object_id='',   # idem
                ip_address=request.META.get('REMOTE_ADDR', None),
                request_url=request.build_absolute_uri(),
                http_method=request.method
            )



from amministratore.models import Contenuto
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin

class ContentCollectorMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Cattura solo pagine HTML normali GET
        if request.method == 'GET' and response.get('Content-Type', '').startswith('text/html'):
            # Escludi URL non rilevanti
            excluded_paths = ['/static/', '/media/', '/admin/', '/admin-secure/']
            if any(request.path.startswith(p) for p in excluded_paths):
                return response  # Non registrare file statici o admin

            try:
                # Analizza il contenuto HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Titolo sicuro (evita .strip() su None)
                page_title = (
                    soup.title.string.strip()
                    if soup.title and soup.title.string
                    else 'Senza Titolo'
                )

                # Testo del body pulito
                body_text = soup.get_text(separator=' ', strip=True)
                body_text = ' '.join(body_text.split())

                # Salva solo se c'è contenuto significativo
                if body_text and len(body_text) > 30:
                    # Controlla se esiste già contenuto per quell'URL
                    existing = Contenuto.objects.filter(url_pagina=request.path).first()
                    if not existing:
                        contenuto = Contenuto(
                            titolo=page_title,
                            contenuto=body_text,
                            url_pagina=request.path,
                            timestamp=datetime.utcnow()
                        )
                        contenuto.save()
            except Exception as e:
                # Logga o ignora errori parsing HTML senza bloccare il sito
                print(f"Errore in ContentCollectorMiddleware: {e}")

        return response

