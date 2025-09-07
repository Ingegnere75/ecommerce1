from django.db import models
from datetime import datetime


class LayoutHome(models.Model):
    html = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Layout salvato il {self.updated_at.strftime('%d/%m/%Y %H:%M')}"


class LayoutElemento(models.Model):
    TIPO_ELEMENTO = [
        ('banner', 'Banner'),
        ('testo', 'Testo'),
        ('card', 'Card'),
        ('video', 'Video'),
        ('immagine', 'Immagine'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_ELEMENTO)
    contenuto = models.TextField(blank=True, null=True)  # Testo, link, ecc.
    file = models.FileField(upload_to='editor_uploads/', blank=True, null=True)
    pos_x = models.IntegerField()
    pos_y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    z_index = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.tipo} - ({self.pos_x}, {self.pos_y})"


class LayoutSalvato(models.Model):
    pagina = models.CharField(max_length=50, unique=True)
    contenuto = models.TextField()

    def __str__(self):
        return f"Layout salvato per: {self.pagina}"
