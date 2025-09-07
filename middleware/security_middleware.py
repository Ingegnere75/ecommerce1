import re
from django.http import HttpResponseForbidden
from django.shortcuts import render

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_patterns = [
            re.compile(r'(https?:\/\/)?([a-zA-Z0-9\-]+\.)?(malicious|phish|spam)\.'),  # domini esterni pericolosi
            re.compile(r'(bcc:|cc:|%0A|%0D|content-type)', re.IGNORECASE),             # header email injection
        ]
        self.ip_blacklist = set()
        self.request_limit = {}

        # ✅ Percorsi interni del sito che devono sempre essere permessi
        self.excluded_paths = [
            '/accounts/confirm-otp/',
            '/accounts/register/',
            '/accounts/reclami/',
            '/accounts/password_reset/',
            '/accounts/password_reset_request/',
            '/admin/login/',
            '/admin/',
        ]

    def __call__(self, request):
        ip = self._get_client_ip(request)

        # ✅ Escludi i percorsi del flusso interno dal blocco
        if any(request.path.startswith(path) for path in self.excluded_paths):
            return self.get_response(request)

        # ❌ Blocca IP noti
        if ip in self.ip_blacklist:
            return HttpResponseForbidden("Accesso negato.")

        # ❌ Blocca pattern sospetti (solo da esterni o bot)
        referer = request.META.get('HTTP_REFERER', '')
        if not referer.startswith(f"http://{request.get_host()}") and request.method == 'POST':
            for pattern in self.suspicious_patterns:
                if pattern.search(str(request.body)):
                    return render(request, 'errors/phishing_detected.html', status=403)

        # ❌ Blocca loop su email solo da esterni
        if '/email/' in request.path and request.method == 'POST':
            if self._is_spamming(ip):
                return render(request, 'errors/email_loop.html', status=429)

        return self.get_response(request)

    def _get_client_ip(self, request):
        return request.META.get('REMOTE_ADDR', '')

    def _is_spamming(self, ip):
        from time import time
        now = time()
        window = 10
        if ip not in self.request_limit:
            self.request_limit[ip] = [now]
            return False
        self.request_limit[ip] = [t for t in self.request_limit[ip] if now - t < window]
        self.request_limit[ip].append(now)
        return len(self.request_limit[ip]) > 5
