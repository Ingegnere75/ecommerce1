# ✅ 1. MODELLI
# core/models.py
from django.utils.text import slugify
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone
#-----categoria----------------------------------------------------------------------------------


def generate_categoria_code():
    last = Categoria.objects.order_by('-codice').first()
    if not last:
        return '100'
    last_code = int(last.codice)
    return str(last_code + 1).zfill(3)



from django.db import models
from django.utils.text import slugify
from .models import generate_categoria_code  # Assicurati che esista

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    codice = models.CharField(max_length=3, unique=True, blank=True)
    immagine = models.ImageField(upload_to='categorie/', null=True, blank=True)
    larghezza = models.PositiveIntegerField(default=300)
    altezza = models.PositiveIntegerField(default=200)
    descrizione = models.TextField(blank=True)

    # Campi sconto
    is_sconto = models.BooleanField(default=False)
    percentuale_sconto = models.IntegerField(default=0)  # ✅ Intero compatibile con Decimal

    def save(self, *args, **kwargs):
        if not self.codice:
            self.codice = generate_categoria_code()
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.codice}"

    
#----------Sottocategoria------------------------------------------------------------------------------------

def generate_sottocategoria_code(categoria_codice):
    last = SottoCategoria.objects.filter(categoria__codice=categoria_codice).order_by('-codice').first()
    if not last:
        return categoria_codice + '200'
    last_suffix = int(last.codice[-3:])
    new_suffix = str(last_suffix + 1).zfill(3)
    return categoria_codice + new_suffix
   

from django.db import models
from django.utils.text import slugify
from .models import generate_sottocategoria_code  # Assicurati che esista

class SottoCategoria(models.Model):
    categoria = models.ForeignKey(
        'Categoria',
        related_name='sottocategorie',
        on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    codice = models.CharField(max_length=6, unique=True, blank=True)
    immagine = models.ImageField(upload_to='sottocategorie/', null=True, blank=True)
    larghezza = models.PositiveIntegerField(default=300)
    altezza = models.PositiveIntegerField(default=200)
    descrizione = models.TextField(blank=True)
    contenuto_html = models.TextField("Contenuto personalizzato", blank=True)
    contenuto_larghezza = models.PositiveIntegerField("Larghezza contenuto (px)", default=800)
    contenuto_altezza = models.PositiveIntegerField("Altezza contenuto (px)", default=300)
   
    # Sconto sulla sottocategoria
    is_sconto = models.BooleanField(default=False)
    percentuale_sconto = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.codice and self.categoria:
            self.codice = generate_sottocategoria_code(self.categoria.codice)

        if not self.slug:
            base_slug = slugify(self.nome)
            slug = base_slug
            counter = 1
            while SottoCategoria.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} ({self.categoria.nome}) - {self.codice}"



    
    
#-----------------magazzino---------------------------------------------------------------------------------------------

class Magazzino(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    sottocategoria = models.ForeignKey(SottoCategoria, on_delete=models.SET_NULL, null=True, blank=True)
    codice = models.CharField(max_length=10, unique=True, blank=True)
    nome = models.CharField(max_length=100)
    descrizione = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.codice and self.categoria and self.sottocategoria:
            self.codice = generate_magazzino_code(self.categoria.codice, self.sottocategoria.codice)
        elif not self.codice:
            # Fallback: codice base su nome o ID se categoria/sottocategoria mancano
            self.codice = f"GEN-{self.pk or 'NEW'}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.codice}"

def generate_magazzino_code(categoria_codice, sottocategoria_codice):
    base = categoria_codice + sottocategoria_codice[-3:]  # es: 101 + 202 = 101202
    from .models import Prodotto
    last = Prodotto.objects.filter(
        categoria__codice=categoria_codice,
        sottocategoria__codice=sottocategoria_codice
    ).order_by('-codice_magazzino').first()

    if not last or not last.codice_magazzino:
        return base + '3000'

    last_suffix = int(last.codice_magazzino[-4:])
    new_suffix = str(last_suffix + 1).zfill(4)
    return base + new_suffix


#-------prodotto-----------------------------------------------------------------------------------------------------

from django.db import models
from django.core.exceptions import ValidationError

TAGLIE_EUROPEE = [
    ('XS', 'XS (34 EU)'),
    ('S', 'S (36 EU)'),
    ('M', 'M (38 EU)'),
    ('L', 'L (40 EU)'),
    ('XL', 'XL (42 EU)'),
    ('XXL', 'XXL (44 EU)'),
    ('XXXL', 'XXXL (46 EU)'),
]

MISURE_STANDARD = [
    ('38', '38'),
    ('40', '40'),
    ('42', '42'),
    ('44', '44'),
    ('46', '46'),
    ('48', '48'),
    ('50', '50'),
    ('52', '52'),
    ('54', '54'),
    ('56', '56'),
    ('58', '58'),
    ('60', '60'),

]

from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils.text import slugify

# Presumo che TAGLIE_EUROPEE e MISURE_STANDARD siano già definiti altrove

class Prodotto(models.Model):
    codice_prodotto = models.CharField(max_length=20, unique=True)
    codice_magazzino = models.CharField(max_length=13, unique=True, blank=True, null=True)
    nome = models.CharField(max_length=100)
    descrizione = models.TextField()
    prezzo = models.DecimalField(max_digits=10, decimal_places=2)
    disponibilita = models.PositiveIntegerField()
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    sottocategoria = models.ForeignKey('SottoCategoria', on_delete=models.CASCADE, null=True, blank=True)
    immagine = models.ImageField(upload_to='prodotti/')
    altezza = models.PositiveIntegerField(default=300)
    larghezza = models.PositiveIntegerField(default=200)

    # ✅ Tavolozza dei colori
    colorazioni = models.CharField(max_length=255, blank=True, help_text="Inserisci i codici colore HEX separati da virgola, es. #FF0000,#00FF00")

    # ✅ Scelte predefinite
    taglia = models.CharField(max_length=5, choices=TAGLIE_EUROPEE, blank=True, null=True)
    misura = models.CharField(max_length=5, choices=MISURE_STANDARD, blank=True, null=True)

    # ✅ Scontistica
    is_sconto = models.BooleanField(default=False)
    percentuale_sconto = models.IntegerField(default=0)

    # ✅ Extra immagini e descrizioni
    for i in range(1, 9):
        vars()[f'immagine_extra_{i}'] = models.ImageField(upload_to='prodotti_extra/', blank=True, null=True)
        vars()[f'altezza_extra_{i}'] = models.PositiveIntegerField(default=300, blank=True, null=True)
        vars()[f'larghezza_extra_{i}'] = models.PositiveIntegerField(default=200, blank=True, null=True)
        vars()[f'descrizione_{i}'] = models.TextField(blank=True, null=True)
        vars()[f'altezza_descrizione_{i}'] = models.PositiveIntegerField(default=300)
        vars()[f'larghezza_descrizione_{i}'] = models.PositiveIntegerField(default=200)

    # ✅ Video & Documento
    video_1 = models.FileField(upload_to='video_prodotti/', blank=True, null=True)
    altezza_video_1 = models.PositiveIntegerField(default=360, blank=True, null=True)
    larghezza_video_1 = models.PositiveIntegerField(default=640, blank=True, null=True)

    video_2 = models.FileField(upload_to='video_prodotti/', blank=True, null=True)
    altezza_video_2 = models.PositiveIntegerField(default=360, blank=True, null=True)
    larghezza_video_2 = models.PositiveIntegerField(default=640, blank=True, null=True)

    documento_1 = models.FileField(upload_to='documenti_prodotti/', blank=True, null=True)

    testo_aggiuntivo = models.TextField(blank=True, null=True)
    altezza_testo = models.PositiveIntegerField(default=100, blank=True, null=True)
    larghezza_testo = models.PositiveIntegerField(default=300, blank=True, null=True)

    def save(self, *args, **kwargs):
        if Prodotto.objects.filter(codice_prodotto=self.codice_prodotto).exclude(pk=self.pk).exists():
            raise ValidationError("⚠️ Il codice prodotto esiste già. Inserisci un codice diverso.")

        if not self.codice_magazzino and self.categoria and self.sottocategoria:
            base = self.categoria.codice + self.sottocategoria.codice[-3:]
            suffix = 3000
            while True:
                codice_generato = base + str(suffix).zfill(4)
                if not Prodotto.objects.filter(codice_magazzino=codice_generato).exclude(pk=self.pk).exists():
                    self.codice_magazzino = codice_generato
                    break
                suffix += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.codice_prodotto} - {self.codice_magazzino}"

    @property
    def prezzo_scontato(self):
        """
        Calcola il prezzo scontato seguendo la priorità:
        1. Sconto sul prodotto
        2. Sconto sulla sottocategoria
        3. Sconto sulla categoria
        """
        if self.is_sconto and self.percentuale_sconto > 0:
            return self.prezzo * (Decimal('1') - Decimal(self.percentuale_sconto) / Decimal('100'))
        elif self.sottocategoria and self.sottocategoria.is_sconto and self.sottocategoria.percentuale_sconto > 0:
            return self.prezzo * (Decimal('1') - Decimal(self.sottocategoria.percentuale_sconto) / Decimal('100'))
        elif self.categoria and self.categoria.is_sconto and self.categoria.percentuale_sconto > 0:
            return self.prezzo * (Decimal('1') - Decimal(self.categoria.percentuale_sconto) / Decimal('100'))
        return self.prezzo





#-----------home elemento--------------------------------------------------------------------------------------



class HomeElemento(models.Model):
    ZONA_SCELTA = [
        ('hero', 'Hero'),
        ('center', 'Centro'),
        ('bottom', 'Fondo'),
        ('custom', 'Custom'),
    ]
    TIPO = [
        ('testo', 'Testo'),
        ('immagine', 'Immagine'),
        ('video', 'Video'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO)
    zona = models.CharField(max_length=20, choices=ZONA_SCELTA, default='center')
    titolo = models.CharField(max_length=100, blank=True, null=True)
    contenuto_testo = models.TextField(blank=True, null=True)

    immagine = models.ImageField(upload_to='elementi/', blank=True, null=True)
    video = models.FileField(upload_to='elementi/', blank=True, null=True)

    larghezza = models.PositiveIntegerField(blank=True, null=True)
    altezza = models.PositiveIntegerField(blank=True, null=True)
    ordine = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.zona} - {self.tipo} - {self.titolo or 'Senza titolo'}"

    class Meta:
        ordering = ['zona', 'ordine']


#--------------carrello-----------------------------------------------------------------------------------


from django.db import models
from django.contrib.auth.models import User
from datetime import date

class CodiceSconto(models.Model):
    codice = models.CharField(max_length=50, unique=True)
    percentuale = models.IntegerField()  # ← CAMBIATO da DecimalField a IntegerField
    attivo = models.BooleanField(default=True)
    scadenza = models.DateField(null=True, blank=True)
    utente = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    multiuso = models.BooleanField(default=False)
    usato = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.codice} - {self.percentuale}%"

    def is_valido(self):
        oggi = date.today()
        if not self.attivo:
            return False
        if self.scadenza and self.scadenza < oggi:
            return False
        if self.usato and not self.multiuso:
            return False
        return True



class Carrello(models.Model):
    sessione = models.CharField(max_length=100, unique=True)
    creato_il = models.DateTimeField(auto_now_add=True)
    codice_sconto = models.ForeignKey('CodiceSconto', on_delete=models.SET_NULL, null=True, blank=True)
    prezzo_spedizione = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.sessione

    def get_subtotale(self):
        """Calcola il subtotale del carrello usando i prezzi scontati."""
        return sum(item.get_subtotale for item in self.carrelloitem_set.all())

    def get_totale(self):
        """Calcola il totale del carrello: subtotale - sconto + spedizione."""
        totale_articoli = self.get_subtotale()
        totale_sconto = Decimal('0.00')

        if self.codice_sconto and self.codice_sconto.attivo:
            totale_sconto = (totale_articoli * self.codice_sconto.percentuale) / Decimal('100')

        return totale_articoli - totale_sconto + self.prezzo_spedizione


class CarrelloItem(models.Model):
    carrello = models.ForeignKey('Carrello', on_delete=models.CASCADE)
    prodotto = models.ForeignKey('Prodotto', on_delete=models.CASCADE)
    quantita = models.PositiveIntegerField(default=1)

    @property
    def get_subtotale(self):
        return self.prodotto.prezzo_scontato * self.quantita






#--------------------------------------------------------------------------------------------------------------






#------------prezzo----------------------------------------------------------------------------------------------
from django.db import models
from django.contrib.auth.models import User

class PrezzoSpedizione(models.Model):
    nome = models.CharField(max_length=100)
    prezzo = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.nome} - € {self.prezzo}"




#------------ordine-------------------------------------------------------------------------------------------------------


from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Prodotto
from core.models import PrezzoSpedizione  # o da dove proviene il modello

class Ordine(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    codice_ordine = models.CharField(max_length=100, unique=True, blank=True, null=True)
    is_guest = models.BooleanField(default=False)

    # Contatti
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    codice_fiscale = models.CharField(max_length=30)

    # Spedizione
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=255)
    civico = models.CharField(max_length=10)
    cap = models.CharField(max_length=10)
    citta = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)

    # Prezzo spedizione
    prezzo_spedizione = models.ForeignKey(PrezzoSpedizione, null=True, blank=True, on_delete=models.SET_NULL)
    totale_pagare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Fatturazione
    fatturazione_diversa = models.BooleanField(default=False)
    nome_fatt = models.CharField(max_length=100, blank=True, null=True)
    cognome_fatt = models.CharField(max_length=100, blank=True, null=True)
    indirizzo_fatt = models.CharField(max_length=255, blank=True, null=True)
    civico_fatt = models.CharField(max_length=10, blank=True, null=True)
    cap_fatt = models.CharField(max_length=10, blank=True, null=True)
    citta_fatt = models.CharField(max_length=100, blank=True, null=True)
    provincia_fatt = models.CharField(max_length=100, blank=True, null=True)
    email_inviata = models.BooleanField(default=False)
    carrello_sessione = models.CharField(max_length=100, blank=True, null=True)

    # Pagamento
    pagato = models.BooleanField(default=False)

    # Stato ordine
    data_creazione = models.DateTimeField(auto_now_add=True)
    stato = models.CharField(max_length=20, choices=[
        ('in_attesa', 'In attesa'),
        ('spedito', 'Spedito'),
        ('consegnato', 'Consegnato'),
    ], default='in_attesa')

    # Sconti
    codice_sconto = models.CharField(max_length=20, blank=True, null=True)
    sconto_percentuale = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.codice_ordine or f"Ordine #{self.pk}"

    def get_totale(self):
        totale = sum(item.get_subtotale() for item in self.ordineitem_set.all())
        if self.sconto_percentuale:
            totale -= (totale * Decimal(self.sconto_percentuale) / 100)
        if self.prezzo_spedizione:
            totale += Decimal(self.prezzo_spedizione.prezzo)
        return round(totale, 2)


from django.db import models
from decimal import Decimal

class OrdineItem(models.Model):
    ordine = models.ForeignKey('Ordine', on_delete=models.CASCADE)
    prodotto = models.ForeignKey('Prodotto', on_delete=models.CASCADE)
    quantita = models.PositiveIntegerField(default=1)
    prezzo_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    pagato = models.BooleanField(default=False)
    data_acquisto = models.DateTimeField(default=timezone.now)  # ← AGGIUNTO


    def __str__(self):
        return f"{self.quantita} x {self.prodotto.nome}"

    def get_subtotale(self):
        return self.prezzo_unitario * self.quantita








#--------------------------------------------------------------------------------------------------------------------






#-----banner--------------------------------------------------------------------------------------------------------------



class Banner(models.Model):
    titolo = models.CharField(max_length=100)
    immagine = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True)
    attivo = models.BooleanField(default=True)
    altezza = models.PositiveIntegerField(default=300)  # Default height
    larghezza = models.PositiveIntegerField(default=800)  # Default width

    def __str__(self):
        return self.titolo


# core/models.py
from django.db import models

class ImmaginePersonalizzata(models.Model):
    titolo = models.CharField(max_length=100)
    descrizione = models.TextField(blank=True)
    immagine = models.ImageField(upload_to='immagini_personalizzate/')
    altezza = models.PositiveIntegerField(default=400)  # Altezza dell'immagine in pixel
    larghezza = models.PositiveIntegerField(default=600)  # Larghezza dell'immagine in pixel
    attivo = models.BooleanField(default=True)

    def __str__(self):
        return self.titolo





from django.db import models

class HomeBanner(models.Model):
    ZONE_CHOICES = [
        ('hero', 'Hero Zone (in alto)'),
        ('center', 'Center Zone (centrale)'),
        ('bottom', 'Bottom Zone (in basso)'),
    ]

    titolo = models.CharField(max_length=100, blank=True, null=True)
    sottotitolo = models.CharField(max_length=255, blank=True, null=True)
    testo_bottone = models.CharField(max_length=100, blank=True, null=True)
    font_titolo = models.CharField(max_length=100, blank=True, null=True)
    font_color = models.CharField(max_length=7, blank=True, null=True, default="#000000")  # es: #000000
    colore_bottone = models.CharField(max_length=7, blank=True, null=True, default="#ffffff")
    immagine = models.ImageField(upload_to='banner/', blank=True, null=True)
    immagine_sfondo = models.ImageField(upload_to='banner/', blank=True, null=True)
    video = models.FileField(upload_to='banner/', blank=True, null=True)
    larghezza = models.PositiveIntegerField(blank=True, null=True)
    altezza = models.PositiveIntegerField(blank=True, null=True)
    posizione = models.CharField(max_length=10, choices=ZONE_CHOICES, default='hero')
    visibile = models.BooleanField(default=True)

    def __str__(self):
        return str(self.titolo) if self.titolo else f"Banner #{self.pk}"


#-------------cards------------------------------------------------------------------------------------------------

class CardSezione(models.Model):
    titolo = models.CharField(max_length=200, default="New Collections")
    sottotitolo = models.TextField(blank=True, null=True)
    classe_titolo = models.CharField(max_length=100, blank=True, null=True, help_text="Esempio: fw-bold fs-1 text-primary")
    classe_sottotitolo = models.CharField(max_length=100, blank=True, null=True, help_text="Esempio: text-muted fs-6")
    testo_extra = models.TextField(blank=True, null=True)
    font_family = models.CharField(max_length=100, blank=True, null=True, help_text="Esempio: 'Playfair Display', cursive")
    
    def __str__(self):
        return self.titolo


class HomeCard(models.Model):
    titolo = models.CharField(max_length=100)
    descrizione = models.CharField(max_length=200, blank=True)
    immagine = models.ImageField(upload_to='homecards/', help_text="Puoi caricare anche immagini già presenti in static/images se le inserisci manualmente")
    link_custom = models.URLField(blank=True, null=True)
    categoria_collegata = models.ForeignKey('Categoria', blank=True, null=True, on_delete=models.SET_NULL)
    prodotto_collegato = models.ForeignKey('Prodotto', blank=True, null=True, on_delete=models.SET_NULL)
    larghezza = models.PositiveIntegerField(default=400)
    altezza = models.PositiveIntegerField(default=300)

    def __str__(self):
        return self.titolo

    def get_link(self):
        if self.link_custom:
            return self.link_custom
        elif self.categoria_collegata:
            return reverse('dettaglio_categoria', args=[self.categoria_collegata.slug])
        elif self.prodotto_collegato:
            return reverse('dettaglio_prodotto', args=[self.prodotto_collegato.pk])
        return "#"



#----------------layout---------------------------------------------------------------------------------------

class LayoutElemento(models.Model):
    html = models.TextField()
    tipo = models.CharField(max_length=50)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    width = models.FloatField(default=300)
    height = models.FloatField(default=150)
    ordine = models.IntegerField(default=0)
    data_creazione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} ({self.x}, {self.y})"


from django.db import models


class LayoutSalvato(models.Model):
    contenuto = models.TextField()
    salvato_il = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Layout salvato il {self.salvato_il.strftime('%d/%m/%Y %H:%M:%S')}"


class LayoutHome(models.Model):
    contenuto_html = models.TextField()
    aggiornato_il = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Layout aggiornato il {self.aggiornato_il.strftime('%d/%m/%Y %H:%M:%S')}"

#---------------------brand------------------------------------------------------------------------------------------------------------

class Brand(models.Model):
    nome = models.CharField(max_length=100)
    descrizione = models.TextField(blank=True)

    colore_testo = models.CharField(max_length=20, default='#000000')
    font_brand = models.CharField(max_length=100, default='Arial')

    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)

    link = models.URLField(blank=True, null=True, help_text="Link ufficiale del brand (opzionale)")

    attivo = models.BooleanField(default=True, help_text="Se selezionato, il brand sarà visibile nel sito.")

    def __str__(self):
        return self.nome



class ContattiBrand(models.Model):
    nome = models.CharField(max_length=100, default="Kaira Shop")
    indirizzo = models.CharField(max_length=200, default="Via Nettunia 77")
    cap_citta = models.CharField(max_length=100, default="84045 Altavilla Silentina, SA")
    partita_iva = models.CharField(max_length=100, default="0001587963")
    logo = models.ImageField(upload_to='pagine/', blank=True, null=True)
    email = models.EmailField(default="info@kaira.it")
    telefono = models.CharField(max_length=20, default="+39 320 000 0000")

    def __str__(self):
        return f"Contatti di {self.nome}"

#--------pagina informativa----------------------------------------------------------------------------------------------------------------

class Informativa(models.Model):
    SLUG_CHOICES = [
        ('chi-siamo', 'Chi Siamo'),
        ('sostenibilita', 'Sostenibilità'),
    ]

    slug = models.SlugField(choices=SLUG_CHOICES, unique=True)
    titolo = models.CharField(max_length=100)
    immagine = models.ImageField(upload_to='informative/', null=True, blank=True)
    banner = models.ImageField(upload_to='informative/', null=True, blank=True)
    contenuto = models.TextField()
    video = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.titolo





class PaginaInformativa(models.Model):
    titolo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    contenuto_testo = CKEditor5Field('Testo', config_name='default')
    immagine = models.ImageField(upload_to='pagine/', blank=True, null=True)
    video = models.FileField(upload_to='pagine/video/', blank=True, null=True)
    pdf = models.FileField(upload_to='pagine/pdf/', blank=True, null=True)
    mostra_pdf = models.BooleanField(default=True)

    def __str__(self):
        return self.titolo

#--------------massaggio-------------------------------------------------------------------------------------

class MessaggioContatto(models.Model):
    email = models.EmailField()
    oggetto = models.CharField(max_length=255)
    messaggio = models.TextField()
    allegato = models.FileField(upload_to='allegati/', blank=True, null=True)
    letto = models.BooleanField(default=False)
    data_invio = models.DateTimeField(auto_now_add=True)

#--------------------------------------------------------------------------------------------------------------------

from django.db import models
from django.contrib.auth.models import User

class CookieConsent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    scelta = models.CharField(max_length=20)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user or self.ip_address} - {self.scelta}"


#-----------------------------------------------------------------------------------------------------------------

# core/models.py

from django.db import models
from django.contrib.auth.models import User

# core/models.py


class InteractionLog(models.Model):
    ACTION_TYPES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view', 'View'),   # aggiungiamo anche view!
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=100, null=True, blank=True)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # 🔥 NUOVI CAMPI da aggiungere:
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    request_url = models.URLField(max_length=500, null=True, blank=True)
    http_method = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action_type} - {self.request_url}"








from django.db import models

class StrisciaInfo(models.Model):
    LUOGO_CHOICES = [
        ('footer', 'Footer'),
        ('navbar', 'Navbar'),
    ]

    titolo = models.CharField("Titolo", max_length=100, default="")
    testo = models.CharField("Testo da mostrare", max_length=255)
    attiva = models.BooleanField("Attiva", default=False)
    luogo = models.CharField("Dove mostrare", max_length=20, choices=LUOGO_CHOICES, default='footer')  # ✅ Nuovo campo
    colore_sfondo = models.CharField("Colore di sfondo (es: #0d6efd)", max_length=7, default="#0d6efd")
    colore_testo = models.CharField("Colore del testo (es: #ffffff)", max_length=7, default="#ffffff")
    velocita = models.PositiveIntegerField("Velocità (secondi per ciclo)", default=20, help_text="Valore in secondi. Più basso = più veloce")

    def __str__(self):
        return self.titolo or "Striscia Informativa"



