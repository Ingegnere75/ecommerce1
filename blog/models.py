

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.html import format_html
from core.models import Prodotto  # ✅ IMPORTANTE

class ProdottoSuggerito(models.Model):
    autore = models.ForeignKey(User, on_delete=models.CASCADE)
    titolo = models.CharField(max_length=100)
    descrizione = models.TextField(default='')
    link = models.URLField(blank=True, null=True, help_text="Inserisci il link al prodotto sul sito")  # ✅ AGGIUNGI QUESTO CAMPO

    immagine = models.ImageField(upload_to='correlati/', blank=True, null=True)
    video = models.FileField(upload_to='video_correlati/', blank=True, null=True)

    img_width = models.PositiveIntegerField(blank=True, null=True, verbose_name="Larghezza immagine (px)")
    img_height = models.PositiveIntegerField(blank=True, null=True, verbose_name="Altezza immagine (px)")
    video_width = models.PositiveIntegerField(blank=True, null=True, verbose_name="Larghezza video (px)")
    video_height = models.PositiveIntegerField(blank=True, null=True, verbose_name="Altezza video (px)")

    data_pubblicazione = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.link:
            try:
                prodotto = Prodotto.objects.get(nome__iexact=self.titolo)
                self.link = f"/prodotti/{prodotto.id}/"  # puoi sostituire con reverse('nome_url', args=[prodotto.slug])
            except Prodotto.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titolo

    def link_prodotto(self):
        if self.link:
            return format_html(f"<a href='{self.link}' target='_blank'>Vai al sito</a>")
        return "Nessun link"
    link_prodotto.short_description = "Link prodotto"



class ArticoloBlog(models.Model):
    titolo = models.CharField(max_length=255)
    contenuto = models.TextField()
    contenuto_width = models.PositiveIntegerField(blank=True, null=True, verbose_name="Larghezza contenuto (px)")
    contenuto_height = models.PositiveIntegerField(blank=True, null=True, verbose_name="Altezza contenuto (px)")

    immagine = models.ImageField(upload_to='blog/', blank=True, null=True)
    img_width = models.PositiveIntegerField(blank=True, null=True, verbose_name="Larghezza immagine (px)")
    img_height = models.PositiveIntegerField(blank=True, null=True, verbose_name="Altezza immagine (px)")

    immagine_sfondo = models.ImageField(upload_to='sfondi_blog/', blank=True, null=True)
    sfondo_width = models.PositiveIntegerField(blank=True, null=True, verbose_name="Larghezza sfondo (px)")
    sfondo_height = models.PositiveIntegerField(blank=True, null=True, verbose_name="Altezza sfondo (px)")

    video = models.FileField(upload_to='video_blog/', blank=True, null=True)
    video_width = models.PositiveIntegerField(blank=True, null=True, verbose_name="Larghezza video (px)")
    video_height = models.PositiveIntegerField(blank=True, null=True, verbose_name="Altezza video (px)")

    contorno_card = models.BooleanField(default=True, verbose_name="Contorno visibile")
    prodotti_correlati = models.ManyToManyField(ProdottoSuggerito, blank=True, related_name="articoli_correlati")

    slug = models.SlugField(unique=True)
    data_pubblicazione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titolo


class CommentoBlog(models.Model):
    post = models.ForeignKey(ArticoloBlog, on_delete=models.CASCADE, related_name='commenti')
    utente = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    testo = models.TextField(max_length=250)
    data_pubblicazione = models.DateTimeField(default=timezone.now)

    emoji = models.CharField(
        max_length=10,
        choices=[
            ('👍', 'Like'),
            ('😊', 'Sorriso'),
            ('😮', 'Wow'),
            ('😢', 'Triste'),
        ],
        default='👍'
    )
    risposta_a = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='risposte')

    def __str__(self):
        return f"{self.utente.username} su {self.post.titolo}"




class BannerInformativo(models.Model):
    titolo = models.CharField(max_length=200, default="Scopri il nostro Blog")
    sottotitolo = models.TextField(blank=True, default="Approfondimenti, novità e articoli scritti con passione.")
    testo_bottone = models.CharField(max_length=100, default="Vai al Blog")

    # Nuovi campi
    font_titolo = models.CharField(max_length=100, blank=True, default="Arial", help_text="Font per il titolo")
    colore_bottone = models.CharField(max_length=7, blank=True, default="#007bff", help_text="Colore del bottone in formato HEX (es. #ff0000)")
    font_color = models.CharField(max_length=7, blank=True, default="#000000", help_text="Colore del testo in formato HEX (es. #000000)")

    immagine_sfondo = models.ImageField(upload_to="banner/", blank=True, null=True)
    altezza = models.PositiveIntegerField(default=300, help_text="Altezza del banner in pixel")
    larghezza = models.PositiveIntegerField(default=1200, help_text="Larghezza del banner in pixel")
    visibile = models.BooleanField(default=True)
    data_creazione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titolo
