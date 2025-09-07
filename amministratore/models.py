from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.db import models
from django.utils import timezone
from decimal import Decimal
from core.models import Prodotto  # Importa il modello prodotto
from mongoengine import Document, StringField, DateTimeField
from datetime import datetime, timezone
from mongoengine import Document, StringField, DateTimeField
from datetime import timezone
from django.utils import timezone

#-----------Entrata Magazzino--------------------------------------------------------------------------------------



from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import Prodotto  # Assicurati che sia il percorso giusto

class EntrataMagazzino(models.Model):
    codice_arrivo = models.CharField(max_length=6, unique=True, editable=False)
    codice_magazzino = models.CharField(max_length=50, blank=True)  # Facoltativo
    codice_prodotto = models.CharField(max_length=50)  # Obbligatorio
    nome_prodotto = models.CharField(max_length=100, blank=True)  # Facoltativo

    nome_fornitore = models.CharField(max_length=50)
    cognome_fornitore = models.CharField(max_length=50)
    p_iva = models.CharField(max_length=11)
    nome_societa = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    data_arrivo = models.DateField(default=timezone.now)
    codice_ordine = models.CharField(max_length=50, blank=True)

    quantita = models.PositiveIntegerField(default=0)
    prezzo_con_iva = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    prezzo_trasporto = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    prezzo_totale = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    aggiunto = models.BooleanField(default=False, null=True, help_text="Indicazione manuale, non aggiorna automaticamente il prodotto.")
    link_fornitore = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Inserisci un link al fornitore o alla fattura (facoltativo)."
    )

    def clean(self):
        # Verifica che il prodotto esista nel sistema
        if not Prodotto.objects.filter(codice_prodotto=self.codice_prodotto).exists():
            raise ValidationError(f"⚠️ Prodotto con codice '{self.codice_prodotto}' non trovato. Inseriscilo prima nel sistema.")

    def save(self, *args, **kwargs):
        # Genera automaticamente il codice_arrivo
        if not self.codice_arrivo:
            last = EntrataMagazzino.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.codice_arrivo = str(next_id).zfill(6)

        # Calcolo prezzo totale
        try:
            quantita = int(self.quantita)
            prezzo_con_iva = Decimal(str(self.prezzo_con_iva).replace(',', '.'))
            prezzo_trasporto = Decimal(str(self.prezzo_trasporto).replace(',', '.'))
            self.prezzo_totale = (prezzo_con_iva * quantita) + prezzo_trasporto
        except:
            self.prezzo_totale = Decimal('0.00')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codice_arrivo} - {self.nome_prodotto or 'Prodotto non definito'}"

    class Meta:
        db_table = 'amministratore_entratamagazzino'





#---------------------------------------------------------------------------------------------------------------------------------------


class Contenuto(Document):
    titolo = StringField(required=True)
    contenuto = StringField(required=True)
    url_pagina = StringField(required=True)
    timestamp = DateTimeField(default=lambda: datetime.now(timezone.utc))



class Richiesta(Document):
    richiesta = StringField()
    email_utente = StringField()
    data_richiesta = DateTimeField()
    session_id = StringField()
    risposta = StringField()
    tipo = StringField()             # <--- AGGIUNTO
    pagina_origine = StringField()    # <--- AGGIUNTO


#----------------------------------------------------------------------------------------------------------------------

class PaymentSettings(models.Model):
    # Stripe
    stripe_secret_key = models.CharField("Stripe Secret Key", max_length=255, blank=True, null=True)
    stripe_public_key = models.CharField("Stripe Public Key", max_length=255, blank=True, null=True)

    # PayPal
    paypal_client_id = models.CharField("PayPal Client ID", max_length=255, blank=True, null=True)
    paypal_secret_key = models.CharField("PayPal Secret Key", max_length=255, blank=True, null=True)
    paypal_mode = models.CharField(
        "Modalità PayPal",
        max_length=50,
        choices=[('sandbox', 'Sandbox'), ('live', 'Live')],
        default='sandbox'
    )
    paypal_business_email = models.EmailField("Email Business PayPal", blank=True, null=True)

    # Scalapay
    scalapay_secret_key = models.CharField("Scalapay Secret Key", max_length=255, blank=True, null=True)

    # Email SMTP
    email_host = models.CharField("Email Host", max_length=255, default='smtp.gmail.com')
    email_port = models.PositiveIntegerField("Porta", default=587)
    email_use_tls = models.BooleanField("Usa TLS", default=True)
    email_host_user = models.EmailField("Email mittente", blank=True, null=True)
    email_host_password = models.CharField("Password SMTP", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Impostazione Pagamento"
        verbose_name_plural = "Impostazioni Pagamento"

    def __str__(self):
        return "Configurazione Pagamenti"


# amministratore/models.py

#-----------------------------------------------------------------------------------------------------

class SiteSettings(models.Model):
    maintenance_mode = models.BooleanField(default=False)

    def __str__(self):
        return "Configurazione Sito"



#------------------------------------------------------------------------------------------------------------


class ObiettivoMensile(models.Model):
    mese = models.DateField(default=now)
    utente = models.ForeignKey(User, on_delete=models.CASCADE)

    vendite = models.PositiveIntegerField(default=0)
    ordini = models.PositiveIntegerField(default=0)
    clienti = models.PositiveIntegerField(default=0)
    prodotti = models.PositiveIntegerField(default=0)
    valore_vendite = models.FloatField(default=0)
    conversione = models.FloatField(default=0)
    abbandoni = models.PositiveIntegerField(default=0)
    valore_medio = models.FloatField(default=0)
    prodotto_top = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Obiettivi {self.utente.username} - {self.mese.strftime('%B %Y')}"


#------------------------------------------------------------------------------------------------------------------

