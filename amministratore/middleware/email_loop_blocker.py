import time
import logging
from django.contrib.sessions.models import Session
from django.shortcuts import render

logger = logging.getLogger(__name__)

class EmailLoopBlockerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            # 🔐 LOG l'errore sul backend, ma senza inviare niente
            logger.exception(f"[Middleware] Errore gestito silenziosamente in {request.path}: {e}")
            
            # 🔒 CHIUSURA SESSIONE IMMEDIATA
            if hasattr(request, 'session'):
                request.session.flush()  # rimuove tutti i dati di sessione e rigenera la chiave
            
            # 🔁 Pagina generica di errore, senza dettagli
            return render(request, 'errors/generic_error.html', status=500)
