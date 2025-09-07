from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import ArticoloBlog, CommentoBlog, ProdottoSuggerito


@admin.register(ArticoloBlog)
class ArticoloBlogAdmin(admin.ModelAdmin):
    list_display = ['titolo', 'data_pubblicazione']
    prepopulated_fields = {'slug': ('titolo',)}
    search_fields = ('titolo', 'contenuto')
    readonly_fields = ['data_pubblicazione', 'anteprima_immagine', 'anteprima_sfondo', 'anteprima_video']
    filter_horizontal = ('prodotti_correlati',)

    fieldsets = (
        (None, {
            'fields': ('titolo', 'slug', 'contenuto', 'contenuto_width', 'contenuto_height')
        }),
        ('Media', {
            'fields': (
                'immagine', 'img_width', 'img_height',
                'immagine_sfondo', 'sfondo_width', 'sfondo_height',
                'video', 'video_width', 'video_height',
                'anteprima_immagine', 'anteprima_sfondo', 'anteprima_video',
            )
        }),
        ('Prodotti Collegati', {
            'fields': ('prodotti_correlati',)
        }),
        ('Impostazioni grafiche', {
            'fields': ('contorno_card',)
        }),
        ('Informazioni di sistema', {
            'fields': ('data_pubblicazione',)
        }),
    )

    def anteprima_immagine(self, obj):
        if obj.immagine:
            style = ""
            if obj.img_width:
                style += f"width:{obj.img_width}px;"
            if obj.img_height:
                style += f"height:{obj.img_height}px;"
            return mark_safe(f"<img src='{obj.immagine.url}' style='{style} object-fit:cover; border-radius:0.5rem;' />")
        return "Nessuna immagine"
    anteprima_immagine.short_description = "Anteprima immagine"

    def anteprima_sfondo(self, obj):
        if obj.immagine_sfondo:
            style = ""
            if obj.sfondo_width:
                style += f"width:{obj.sfondo_width}px;"
            if obj.sfondo_height:
                style += f"height:{obj.sfondo_height}px;"
            return mark_safe(f"<img src='{obj.immagine_sfondo.url}' style='{style} object-fit:cover; border-radius:0.5rem;' />")
        return "Nessuno sfondo"
    anteprima_sfondo.short_description = "Anteprima sfondo"

    def anteprima_video(self, obj):
        if obj.video:
            width = obj.video_width or 400
            height = obj.video_height or 300
            return mark_safe(f"""
            <video width='{width}' height='{height}' controls>
                <source src='{obj.video.url}' type='video/mp4'>
                Il tuo browser non supporta il video.
            </video>
            """)
        return "Nessun video"
    anteprima_video.short_description = "Anteprima video"


@admin.register(CommentoBlog)
class CommentoBlogAdmin(admin.ModelAdmin):
    list_display = ('utente', 'post', 'data_pubblicazione', 'emoji')


from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import ProdottoSuggerito

from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import ProdottoSuggerito

@admin.register(ProdottoSuggerito)
class ProdottoSuggeritoAdmin(admin.ModelAdmin):
    list_display = ['autore', 'titolo', 'data_pubblicazione', 'link_prodotto']
    readonly_fields = ['data_pubblicazione', 'anteprima_immagine', 'anteprima_video']

    fieldsets = (
        (None, {
            'fields': ('autore', 'titolo', 'descrizione', 'link')  # ✅ MOSTRA IL CAMPO
        }),
        ('Media', {
            'fields': (
                'immagine', 'img_width', 'img_height',
                'video', 'video_width', 'video_height',
                'anteprima_immagine', 'anteprima_video',
            )
        }),
        ('Sistema', {
            'fields': ('data_pubblicazione',)
        }),
    )

    def anteprima_immagine(self, obj):
        if obj.immagine:
            style = ""
            if obj.img_width:
                style += f"width:{obj.img_width}px;"
            if obj.img_height:
                style += f"height:{obj.img_height}px;"
            return mark_safe(f"<img src='{obj.immagine.url}' style='{style} object-fit:cover; border-radius:0.5rem;' />")
        return "Nessuna immagine"
    anteprima_immagine.short_description = "Anteprima immagine"

    def anteprima_video(self, obj):
        if obj.video:
            width = obj.video_width or 400
            height = obj.video_height or 300
            return mark_safe(f"""
            <video width='{width}' height='{height}' controls>
                <source src='{obj.video.url}' type='video/mp4'>
                Il tuo browser non supporta il video.
            </video>
            """)
        return "Nessun video"
    anteprima_video.short_description = "Anteprima video"


from django.contrib import admin
from .models import BannerInformativo

@admin.register(BannerInformativo)
class BannerInformativoAdmin(admin.ModelAdmin):
    list_display = ("titolo", "visibile", "data_creazione")
    list_filter = ("visibile", "data_creazione")
    search_fields = ("titolo", "sottotitolo", "testo_bottone")
    ordering = ("-data_creazione",)
from django.contrib import admin

# Register your models here.
