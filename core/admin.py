from django.contrib import admin, messages
from .models import (
    Prodotto, Categoria, SottoCategoria, Carrello, CarrelloItem,
    Ordine, Banner, ImmaginePersonalizzata,
    HomeCard, HomeBanner
)


from django.shortcuts import redirect

from .models import HomeElemento  
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin import AdminSite

AdminSite.site_header = 'Gestione Samadafilati'

def link_editor(modeladmin, request, queryset):
    url = reverse("editor_home")
    return redirect(url)
link_editor.short_description = "Vai all'Editor Home"

from .models import HomeElemento

@admin.register(HomeElemento)
class HomeElementoAdmin(admin.ModelAdmin):
    list_display = ['titolo', 'tipo', 'zona', 'ordine']
    list_editable = ['zona', 'ordine']
    list_filter = ['zona', 'tipo']
    search_fields = ['titolo']
    fieldsets = (
        (None, {
            'fields': (
                'zona', 'tipo', 'titolo',
                'contenuto_testo', 'immagine', 'video',
                'larghezza', 'altezza', 'ordine'
            )
        }),
    )

from django.contrib import admin
from .models import Categoria, SottoCategoria, Prodotto
from .forms import SottoCategoriaForm


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'is_sconto', 'percentuale_sconto')
    list_editable = ('is_sconto', 'percentuale_sconto')
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ('nome',)
    ordering = ('nome',)
    list_filter = ('is_sconto',)

from django.contrib import admin
from django import forms
from .models import SottoCategoria

class SottoCategoriaForm(forms.ModelForm):
    class Meta:
        model = SottoCategoria
        fields = '__all__'
        widgets = {
            'contenuto_html': forms.Textarea(attrs={
                'rows': 10,
                'cols': 80,
                'style': 'font-family: monospace; font-size: 14px;'
            }),
            'contenuto_larghezza': forms.NumberInput(attrs={
                'min': 100, 'max': 1600, 'step': 10
            }),
            'contenuto_altezza': forms.NumberInput(attrs={
                'min': 100, 'max': 1000, 'step': 10
            }),
        }

@admin.register(SottoCategoria)
class SottoCategoriaAdmin(admin.ModelAdmin):
    form = SottoCategoriaForm
    list_display = ('nome', 'slug', 'categoria', 'is_sconto', 'percentuale_sconto')
    list_editable = ('is_sconto', 'percentuale_sconto')
    prepopulated_fields = {'slug': ('nome',)}
    list_filter = ('categoria', 'is_sconto')
    search_fields = ('nome',)
    ordering = ('categoria', 'nome')







from django.contrib import admin
from .models import Prodotto
from .forms import ProdottoAdminForm

@admin.register(Prodotto)
class ProdottoAdmin(admin.ModelAdmin):
    form = ProdottoAdminForm

    list_display = (
        'nome',
        'codice_prodotto',
        'categoria',
        'sottocategoria',
        'prezzo',
        'disponibilita',
        'get_taglia_display',
        'get_misura_display',
        'prezzo_scontato_display',
        'is_sconto',
        'percentuale_sconto',
    )

    list_filter = (
        'categoria',
        'sottocategoria',
        'taglia',
        'misura',
        'is_sconto',
    )

    search_fields = (
        'nome',
        'codice_prodotto',
        'descrizione',
        'colorazioni',
        'taglia',
        'misura',
    )

    list_editable = (
        'prezzo',
        'disponibilita',
        'is_sconto',
        'percentuale_sconto',
    )

    readonly_fields = (
        'codice_magazzino',
    )

    ordering = ('nome',)

    fieldsets = (
        ('Informazioni Base', {
            'fields': (
                'nome',
                'codice_prodotto',
                'codice_magazzino',
                'categoria',
                'sottocategoria',
                'descrizione',
                'prezzo',
                'disponibilita',
                'colorazioni',
                'taglia',
                'misura',
                'is_sconto',
                'percentuale_sconto',
            )
        }),
        ('Immagine Principale', {
            'fields': ('immagine', 'altezza', 'larghezza')
        }),
        ('Immagini Extra', {
            'classes': ('collapse',),
            'fields': sum([(
                f'immagine_extra_{i}',
                f'altezza_extra_{i}',
                f'larghezza_extra_{i}',
                f'descrizione_{i}',
                f'altezza_descrizione_{i}',
                f'larghezza_descrizione_{i}',
            ) for i in range(1, 9)], ())
        }),
        ('Video e Documenti', {
            'fields': (
                'video_1', 'altezza_video_1', 'larghezza_video_1',
                'video_2', 'altezza_video_2', 'larghezza_video_2',
                'documento_1',
            )
        }),
        ('Testo Aggiuntivo', {
            'fields': (
                'testo_aggiuntivo',
                'altezza_testo',
                'larghezza_testo',
            )
        }),
    )

    def get_taglia_display(self, obj):
        return obj.get_taglia_display() if obj.taglia else "-"
    get_taglia_display.short_description = 'Taglia'

    def get_misura_display(self, obj):
        return obj.get_misura_display() if obj.misura else "-"
    get_misura_display.short_description = 'Misura'

    def prezzo_scontato_display(self, obj):
        if obj.prezzo_scontato < obj.prezzo:
            return f"€{obj.prezzo_scontato:.2f}"
        return "-"
    prezzo_scontato_display.short_description = "Prezzo Scontato"







#----------------------------------------------------------------------------------------------------------------------



@admin.register(CarrelloItem)
class CarrelloItemAdmin(admin.ModelAdmin):
    list_display = ('carrello', 'prodotto', 'quantita', 'get_subtotale')
    search_fields = ('carrello__id', 'prodotto__nome')

    @admin.display(description='Subtotale')
    def get_subtotale(self, obj):
        return f"€ {obj.subtotale:.2f}"
    
@admin.display(description="Subtotale")
def get_subtotale(self, obj):
    return f"€ {obj.subtotale:.2f}"


#-----------------------------------------------------------------------------------------------------------------------

# Gestione dei Banner

admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('titolo', 'attivo', 'altezza', 'larghezza', 'immagine')
    list_editable = ('attivo', 'altezza', 'larghezza')
    search_fields = ('titolo',)
    list_filter = ('attivo',)

    fieldsets = (
        (None, {
            'fields': ('titolo', 'immagine', 'descrizione', 'attivo', 'altezza', 'larghezza')
        }),
    )

    def immagine_preview(self, obj):
        return f'<img src="{obj.immagine.url}" style="width:100px;" />'
    immagine_preview.allow_tags = True
    immagine_preview.short_description = 'Anteprima Immagine'


# Gestione delle Immagini Personalizzate
@admin.register(ImmaginePersonalizzata)
class ImmaginePersonalizzataAdmin(admin.ModelAdmin):
    list_display = ('titolo', 'altezza', 'larghezza', 'attivo', 'immagine')
    list_editable = ('altezza', 'larghezza', 'attivo')
    search_fields = ('titolo', 'descrizione')
    list_filter = ('attivo',)
    fieldsets = (
        (None, {
            'fields': ('titolo', 'immagine', 'descrizione', 'attivo', 'altezza', 'larghezza')
        }),
    )


# Gestione delle HomeCard
@admin.register(HomeCard)
class HomeCardAdmin(admin.ModelAdmin):
    list_display = ['titolo', 'get_link']


# Gestione dei Banner della Home
from django.contrib import admin
from .models import HomeBanner

@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ['titolo', 'posizione', 'larghezza', 'altezza', 'visibile']
    list_editable = ['posizione', 'larghezza', 'altezza', 'visibile']
    fieldsets = (
        ('Contenuti Banner', {
            'fields': (
                'titolo',
                'sottotitolo',
                'testo_bottone',
                'immagine',
                'immagine_sfondo',
                'video',
            )
        }),
        ('Stile e Layout', {
            'fields': (
                'font_titolo',
                'font_color',
                'colore_bottone',
                'larghezza',
                'altezza',
                'posizione',
                'visibile',
            )
        }),
    )
    search_fields = ['titolo', 'sottotitolo']
    list_filter = ['posizione', 'visibile']




# Gestione degli Ordini con messaggi personalizzati
@admin.register(Ordine)
class OrdineAdmin(admin.ModelAdmin):
    list_display = ('id_colored', 'cliente', 'data_creazione', 'stato', 'totale_ordine')
    list_filter = ('stato',)
    search_fields = ('cliente__username', 'cliente__email')
    list_editable = ('stato',)

    def totale_ordine(self, obj):
        return f"{obj.totale:.2f} €"
    totale_ordine.short_description = "Totale"

    def id_colored(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse

        url = reverse('admin:core_ordine_change', args=[obj.id])
        color = {
            'in_attesa': 'red',
            'spedito': 'black',
            'consegnato': 'blue'
        }.get(obj.stato, 'black')
        return format_html(
            '<a href="{}" style="color:{}; font-weight: bold;">#{} - {}</a>',
            url, color, obj.id, obj.get_stato_display()
        )
    id_colored.short_description = "Ordine"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change and obj.stato == 'in_attesa':
            messages.add_message(request, messages.WARNING, f"⚠️ Nuovo ordine #{obj.id} ricevuto! Da evadere.")
        elif change:
            messages.add_message(request, messages.INFO, f"Ordine #{obj.id} aggiornato a: {obj.stato.upper()}")

from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):
    site_header = "Amministrazione Samadafilati"
    site_title = "Samadafilati"
    index_title = "Gestione"

    def each_context(self, request):
        context = super().each_context(request)
        context['custom_editor_link'] = reverse('editor_home')
        return context

admin_site = MyAdminSite(name='myadmin')

from django.utils.html import format_html
from django.urls import reverse
from .models import LayoutSalvato

@admin.register(LayoutSalvato)
class LayoutSalvatoAdmin(admin.ModelAdmin):
    list_display = ('salvato_il', 'preview_live')

    def preview_live(self, obj):
        return format_html('<a href="{}" class="btn btn-success" target="_blank">👁️ Preview Live</a>', reverse('home'))
    preview_live.short_description = 'Anteprima'

from .models import CardSezione

@admin.register(CardSezione)
class CardSezioneAdmin(admin.ModelAdmin):
    list_display = ('titolo', 'classe_titolo', 'font_family')

from django.contrib import admin
from .models import Brand

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('nome', 'facebook', 'twitter', 'instagram', 'youtube')
    fieldsets = (
        ("Informazioni Generali", {
            'fields': ('nome', 'descrizione', 'logo', 'colore_testo', 'font_brand')
        }),
        ("Social Media", {
            'fields': ('facebook', 'twitter', 'instagram', 'youtube')
        }),
    )



from .models import Informativa

@admin.register(Informativa)
class InformativaAdmin(admin.ModelAdmin):
    list_display = ['titolo', 'slug']


from django.contrib import admin
from django.contrib.admin.sites import AdminSite

class MyAdminSite(AdminSite):
    site_header = 'Gestione Kaira'
    site_title = 'Kaira Admin'
    index_title = 'Amministrazione sito'

    def each_context(self, request):
        context = super().each_context(request)
        context['extra_css'] = ['css/admin_custom.css']
        return context

admin_site = MyAdminSite(name='myadmin')





# core/admin.py

from core.models import MessaggioContatto
from django.shortcuts import render

def admin_messaggi(request):
    messaggi = MessaggioContatto.objects.all().order_by('-data_invio')
    return render(request, 'core/admin_messaggi.html', {'messaggi': messaggi})




from .models import PaginaInformativa

@admin.register(PaginaInformativa)
class PaginaInformativaAdmin(admin.ModelAdmin):
    list_display = ('titolo', 'slug')
    prepopulated_fields = {'slug': ('titolo',)}


from .models import ContattiBrand

admin.site.register(ContattiBrand)


# admin.py
from django.contrib import admin
from .models import PrezzoSpedizione, CodiceSconto














from .models import StrisciaInfo

@admin.register(StrisciaInfo)
class StrisciaInfoAdmin(admin.ModelAdmin):
    list_display = ('titolo', 'testo', 'attiva', 'luogo', 'colore_sfondo', 'colore_testo', 'velocita')
    list_editable = ('attiva', 'luogo')
