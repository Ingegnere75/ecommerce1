from django.db import models
import random
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Prodotto  # o l'app che contiene Prodotto



#-----------------------------------------------------------------------------------------------------------

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=255)
    civico = models.CharField(max_length=20)
    cap = models.CharField(max_length=5)
    citta = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    codice_fiscale = models.CharField(max_length=16)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.email} - {self.nome} {self.cognome}"

#--------------------------------------------------------------------------------------------------------------

def generate_ticket_number():
    """Genera un numero di ticket univoco a 6 cifre"""
    while True:
        number = random.randint(100000, 999999)
        if not Reclamo.objects.filter(numero_ticket=number).exists():
            return number
#-------------------------------------------------------------------------------------------------------------

STATO_CHOICES = [
    ('aperto', 'Aperto'),
    ('in_lavorazione', 'In lavorazione'),
    ('chiuso', 'Chiuso'),
]

ESITO_CHOICES = [
    ('positivo', 'Positivo'),
    ('negativo', 'Negativo'),
    ('', 'Non definito'),
]

class Reclamo(models.Model):
    utente = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    email = models.EmailField()
    numero_ordine = models.CharField(max_length=50)
    oggetto = models.CharField(max_length=255)
    messaggio = models.TextField()
    allegato = models.FileField(upload_to='reclami_allegati/', null=True, blank=True)
    data_invio = models.DateTimeField(auto_now_add=True)
    numero_ticket = models.PositiveIntegerField(default=generate_ticket_number, unique=True, editable=False)

    # Nuovi campi
    stato = models.CharField(max_length=20, choices=STATO_CHOICES, default='aperto')
    esito = models.CharField(max_length=10, choices=ESITO_CHOICES, blank=True)
    risposta_admin = models.TextField(blank=True, null=True)
    data_risposta = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Reclamo #{self.numero_ticket} - {self.nome} {self.cognome}"
#-----------------------------------------------------------------------------------------------------------------------

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE, related_name='wishlisted_by')
    aggiunto_il = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'prodotto')

    def __str__(self):
        return f"{self.user.username} → {self.prodotto.nome}"

#-----------------------------------------------------------------------------------------------------------------

class Cookie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    scelta = models.CharField(max_length=50)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Cookie di {self.user.username}"
        else:
            return f"Cookie anonimo"
#----------------------------------------------------------------------------------------------------------------
