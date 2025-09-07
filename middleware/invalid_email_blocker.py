import smtplib
from django.shortcuts import redirect

class InvalidEmailBlockerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except smtplib.SMTPRecipientsRefused:
            # Caso: indirizzo email inesistente
            request.session.flush()  # ❌ Distrugge tutta la sessione
            return redirect('home')  # 🔇 Silenzioso: reindirizza a home

        except smtplib.SMTPDataError as e:
            if '550' in str(e):
                request.session.flush()
                return redirect('home')

        except smtplib.SMTPException:
            # Qualsiasi altro errore email generico
            request.session.flush()
            return redirect('home')

        # Altri errori non gestiti passano oltre
