import re
from django.http import HttpResponseServerError
from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)

class SafeExternalControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.blocked_domains = [
            r"mailinator\.com",
            r"phishing-site\.com",
            r"tempmail",
        ]

    def __call__(self, request):
        if request.method == 'POST':
            email = request.POST.get('email', '')
            for pattern in self.blocked_domains:
                if re.search(pattern, email):
                    return render(request, "errors/email_blocked.html", status=403)

        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.error(f"[Middleware] Eccezione intercettata: {exception}")

        if "smtplib" in str(type(exception)) or "email" in str(type(exception)):
            return render(request, "errors/email_loop.html", status=500)
        if "requests" in str(type(exception)) and "ConnectionError" in str(exception):
            return render(request, "errors/external_block.html", status=502)
        return None
