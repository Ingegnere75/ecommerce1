from core.services.logger_mongo import LogEvento

def registra_evento(request, sezione, azione, dettagli=None):
    if dettagli is None:
        dettagli = {}

    LogEvento(
        sezione=sezione,
        azione=azione,
        dettagli=dettagli,
        utente_email=request.user.email if request.user.is_authenticated else None,
        utente_username=request.user.username if request.user.is_authenticated else None,
        session_key=request.session.session_key
    ).save()
