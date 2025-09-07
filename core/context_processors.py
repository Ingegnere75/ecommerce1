from .models import Carrello, CarrelloItem, Brand, ContattiBrand

def carrello_context(request):
    if not request.session.session_key:
        request.session.create()
    sessione = request.session.session_key
    carrello, _ = Carrello.objects.get_or_create(sessione=sessione)
    numero_elementi = CarrelloItem.objects.filter(carrello=carrello).count()
    return {
        'carrello_totale_elementi': numero_elementi
    }

def brand_context(request):
    brand = Brand.objects.first()
    return {'brand': brand}

def contatti_brand_context(request):
    contatti_brand = ContattiBrand.objects.first()
    return {'contatti_brand': contatti_brand}







from .models import StrisciaInfo
from amministratore.models import SiteSettings

def striscia_info(request):
    settings = SiteSettings.objects.first()

    if settings and settings.maintenance_mode:
        # Mostra solo un messaggio di manutenzione (sfondo rosso)
        return {
            'striscia_info_footer': {
                'testo': "🚧 <strong>Il sito è attualmente in manutenzione.</strong> Torna a trovarci più tardi.",
                'colore_sfondo': '#FF0000',  # rosso acceso
                'colore_testo': '#FFFFFF',   # bianco
                'velocita': 5,
            },
            'striscia_info_navbar': None
        }

    # Normale gestione delle strisce attive
    strisce_footer = StrisciaInfo.objects.filter(attiva=True, luogo='footer')
    strisce_navbar = StrisciaInfo.objects.filter(attiva=True, luogo='navbar')

    testo_footer = " ".join(
        [f"📌 <strong>{s.titolo}:</strong> {s.testo}" for s in strisce_footer]
    )
    testo_navbar = " ".join(
        [f"📌 <strong>{s.titolo}:</strong> {s.testo}" for s in strisce_navbar]
    )

    return {
        'striscia_info_footer': {
            'testo': testo_footer,
            'colore_sfondo': strisce_footer[0].colore_sfondo if strisce_footer else '',
            'colore_testo': strisce_footer[0].colore_testo if strisce_footer else '',
            'velocita': strisce_footer[0].velocita if strisce_footer else 20,
        } if strisce_footer else None,

        'striscia_info_navbar': {
            'testo': testo_navbar,
            'colore_sfondo': strisce_navbar[0].colore_sfondo if strisce_navbar else '',
            'colore_testo': strisce_navbar[0].colore_testo if strisce_navbar else '',
            'velocita': strisce_navbar[0].velocita if strisce_navbar else 20,
        } if strisce_navbar else None
    }
