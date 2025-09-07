from django.shortcuts import redirect
from django.urls import resolve, Resolver404

class BloccoAccessoGlobaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.eccezioni = [
            'home', 'login', 'logout', 'register',
            'static', 'admin:login', 'admin:index',
            'chi_siamo', 'faq', 'cookie', 'privacy',
            'spedizione', 'resi', 'sostenibilita',
            'termini_condizioni', 'trattamento_dati',
            'informativa_privacy', 'pagamenti',
            'successo', 'admin_login', 'confirm_otp',
            'password_reset_request',
            'pagina_dinamica'  # ✅ questa è la chiave per le pagine dinamiche nel footer
        ]

    def __call__(self, request):
        try:
            resolver_match = resolve(request.path_info)
            view_name = resolver_match.url_name or ''
        except Resolver404:
            return redirect('home')

        # Se è una view tra le eccezioni o è admin, consenti
        if view_name in self.eccezioni or request.path.startswith('/admin/'):
            return self.get_response(request)

        # Controllo referer (opzionale: puoi anche rimuoverlo se dà problemi)
        referer = request.META.get('HTTP_REFERER', '')
        host = request.get_host()
        if view_name != 'successo' and host not in referer:
            return redirect('home')

        # Proteggi solo percorsi riservati
        if request.path.startswith('/accounts/') or request.path.startswith('/amministratore/'):
            if not request.user.is_authenticated:
                return redirect('login')

        return self.get_response(request)
