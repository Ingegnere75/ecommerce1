from django import forms
from core.models import Prodotto  # ✅ NON 'amministratore.models'
from .models import EntrataMagazzino
from core.models import ContattiBrand
from core.models import SottoCategoria
from core.models import Categoria
from  core.models import Brand

from core.models import HomeElemento

from core.models import HomeCard, HomeBanner
#--------------------------------------------------------------------------------------------
#        prodotto form
#------------------------------------------------------------------------------------------------------
from django import forms
from core.models import Prodotto
from core.widgets import ColoriPreviewWidget
from core.colori import COLORI_NOMI



class ProdottoForm(forms.ModelForm):
    class Meta:
        model = Prodotto
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['codice_magazzino'].required = False
        self.fields['codice_magazzino'].widget.attrs['readonly'] = True

#----------------------------------------------------------------------------------------------------------------
#          entrata magazzino forms
#--------------------------------------------------------------------------------------------------------------------------



from django import forms
from .models import EntrataMagazzino

class EntrataMagazzinoForm(forms.ModelForm):
    class Meta:
        model = EntrataMagazzino
        exclude = ['prezzo_totale']  # ✅ Escluso perché calcolato in models.py
        widgets = {
            'aggiunto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Eventuali pulizie personalizzate (opzionali)
        return cleaned_data




#-----------------------------------------------------------------------------------------------
#          contatti brand forms
#--------------------------------------------------------------------------------------------------------




from core.models import ContattiBrand

class ContattiBrandForm(forms.ModelForm):
    class Meta:
        model = ContattiBrand
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control form-control-lg shadow-sm'}),
            'indirizzo': forms.TextInput(attrs={'class': 'form-control shadow-sm'}),
            'cap_citta': forms.TextInput(attrs={'class': 'form-control shadow-sm'}),
            'partita_iva': forms.TextInput(attrs={'class': 'form-control shadow-sm'}),
            'email': forms.EmailInput(attrs={'class': 'form-control shadow-sm'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control shadow-sm'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


#----------------------------------------------------------------------------------------------------------
#          categorie
#--------------------------------------------------------------------------------------------------------------------



from django import forms
from core.models import Categoria

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descrizione', 'immagine', 'larghezza', 'altezza']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descrizione': forms.Textarea(attrs={'class': 'form-control'}),
            'immagine': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'larghezza': forms.NumberInput(attrs={'class': 'form-control'}),
            'altezza': forms.NumberInput(attrs={'class': 'form-control'}),
        }

#------------------------------------------------------------------------------------------------------------------------
#         sottocategorie
#----------------------------------------------------------------------------------------------------------------------------------




from django import forms
from  core.models import SottoCategoria

class SottoCategoriaForm(forms.ModelForm):
    class Meta:
        model = SottoCategoria
        fields = '__all__'
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select shadow-sm'}),
            'nome': forms.TextInput(attrs={'class': 'form-control shadow-sm'}),
            'slug': forms.TextInput(attrs={'class': 'form-control shadow-sm'}),
            'codice': forms.TextInput(attrs={'class': 'form-control shadow-sm'}),
            'immagine': forms.ClearableFileInput(attrs={'class': 'form-control shadow-sm'}),
            'larghezza': forms.NumberInput(attrs={'class': 'form-control shadow-sm'}),
            'altezza': forms.NumberInput(attrs={'class': 'form-control shadow-sm'}),
            'contenuto_larghezza': forms.NumberInput(attrs={'class': 'form-control shadow-sm'}),
            'contenuto_altezza': forms.NumberInput(attrs={'class': 'form-control shadow-sm'}),
            'descrizione': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
            'contenuto_html': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 4}),
            'is_sconto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'percentuale_sconto': forms.NumberInput(attrs={
                'class': 'form-control shadow-sm',
                'min': 0,
                'max': 100,
                'placeholder': 'Inserisci la percentuale di sconto'
            }),
        }



#-------------------------------------------------------------------------------------------------------------------
#          brand
#----------------------------------------------------------------------------------------------------------------------



class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descrizione': forms.Textarea(attrs={'class': 'form-control'}),
            'colore_testo': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'font_brand': forms.TextInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'youtube': forms.URLInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
            'attivo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

#----------gestione home-----------------------------------------------------------------------------------------------------------------------



from django import forms
from  core.models import HomeCard, HomeBanner

class HomeCardForm(forms.ModelForm):
    class Meta:
        model = HomeCard
        fields = '__all__'

from django import forms
from core.models import HomeBanner

class HomeBannerForm(forms.ModelForm):
    class Meta:
        model = HomeBanner
        fields = [
            'titolo',
            'sottotitolo',
            'testo_bottone',
            'font_titolo',
            'font_color',
            'colore_bottone',
            'immagine',
            'immagine_sfondo',
            'video',
            'larghezza',
            'altezza',
            'posizione',
            'visibile',
        ]
        widgets = {
            'font_titolo': forms.TextInput(attrs={'placeholder': 'Esempio: Arial, Roboto, etc.'}),
            'testo_bottone': forms.TextInput(attrs={'placeholder': 'Es: Scopri di più'}),
            'font_color': forms.TextInput(attrs={'type': 'color'}),
            'colore_bottone': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super(HomeBannerForm, self).__init__(*args, **kwargs)
        # Tutti i campi facoltativi lato form
        for field_name in self.fields:
            self.fields[field_name].required = False




class HomeElementoForm(forms.ModelForm):
    class Meta:
        model = HomeElemento
        fields = '__all__'
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'zona': forms.Select(attrs={'class': 'form-select'}),
            'titolo': forms.TextInput(attrs={'class': 'form-control'}),
            'contenuto_testo': forms.Textarea(attrs={'class': 'form-control'}),
            'immagine': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'larghezza': forms.NumberInput(attrs={'class': 'form-control'}),
            'altezza': forms.NumberInput(attrs={'class': 'form-control'}),
            'ordine': forms.NumberInput(attrs={'class': 'form-control'}),
        }
#---------------------------------------------------------------------------------------------------------------------------------        
#----------------------reclamoform-------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------

from accounts.models import Reclamo

class ReclamoAdminForm(forms.ModelForm):
    class Meta:
        model = Reclamo
        fields = ['stato', 'esito', 'risposta_admin']
        labels = {
            'stato': 'Stato del Reclamo',
            'esito': 'Esito',
            'risposta_admin': 'Risposta dell\'Amministratore'
        }


# ✅ forms.py
from django import forms
from core.models import PrezzoSpedizione, CodiceSconto
from django.contrib.auth.models import User

class PrezzoSpedizioneForm(forms.ModelForm):
    class Meta:
        model = PrezzoSpedizione
        fields = ['prezzo']


#----------------------------------------------------------------------------------------------------------

from django import forms
from amministratore.models import Contenuto, Richiesta

class ContenutoForm(forms.Form):
    titolo = forms.CharField(max_length=255)
    contenuto_completo = forms.CharField(widget=forms.Textarea)
    url_pagina = forms.URLField()

class RichiestaForm(forms.Form):
    richiesta_completa = forms.CharField(widget=forms.Textarea)
    utente_email = forms.EmailField(required=False)

#----------------------------------------------------------------------------------------------------------

from django import forms
from .models import ObiettivoMensile

class ObiettivoForm(forms.ModelForm):
    class Meta:
        model = ObiettivoMensile
        exclude = ['utente']
        widgets = {
            'mese': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'vendite': forms.NumberInput(attrs={'class': 'form-control'}),
            'ordini': forms.NumberInput(attrs={'class': 'form-control'}),
            'clienti': forms.NumberInput(attrs={'class': 'form-control'}),
            'prodotti': forms.NumberInput(attrs={'class': 'form-control'}),
            'valore_vendite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'conversione': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'abbandoni': forms.NumberInput(attrs={'class': 'form-control'}),
            'valore_medio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prodotto_top': forms.NumberInput(attrs={'class': 'form-control'}),
        }



#__________________________________________________________________________________________





from django import forms
from core.models import StrisciaInfo

class StrisciaInfoForm(forms.ModelForm):
    class Meta:
        model = StrisciaInfo
        fields = '__all__'
        widgets = {
            'colore_sfondo': forms.TextInput(attrs={'type': 'color'}),
            'colore_testo': forms.TextInput(attrs={'type': 'color'}),
        }

#---------------------------------------------------------------------------------------------------------------

from django import forms
from blog.models import ArticoloBlog

class ArticoloBlogForm(forms.ModelForm):
    class Meta:
        model = ArticoloBlog
        fields = '__all__'



#-----------------------------------------------------------------------------------------------------


from django import forms
from blog.models import BannerInformativo


class BannerInformativoForm(forms.ModelForm):
    font_titolo = forms.CharField(
        label="Font del titolo",
        required=False,
        help_text="Puoi scegliere un font dalla lista suggerita oppure scriverne uno.",
        widget=forms.TextInput(attrs={'placeholder': 'es. sans-serif'})
    )

    colore_bottone = forms.CharField(
        label="Colore del bottone (HEX)",
        required=False,
        help_text="Inserisci un colore in formato HEX (es. #ff0000).",
        widget=forms.TextInput(attrs={'type': 'color'})
    )

    font_color = forms.CharField(
        label="Colore del testo (HEX)",
        required=False,
        help_text="Inserisci un colore in formato HEX (es. #000000).",
        widget=forms.TextInput(attrs={'type': 'color'})
    )

    class Meta:
        model = BannerInformativo
        fields = [
            'titolo',
            'sottotitolo',
            'testo_bottone',
            'font_titolo',
            'font_color',
            'colore_bottone',
            'immagine_sfondo',
            'altezza',
            'larghezza',
            'visibile'
        ]

        widgets = {
            'titolo': forms.TextInput(attrs={'class': 'form-control'}),
            'sottotitolo': forms.TextInput(attrs={'class': 'form-control'}),
            'testo_bottone': forms.TextInput(attrs={'class': 'form-control'}),
            'altezza': forms.NumberInput(attrs={'class': 'form-control', 'min': 50}),
            'larghezza': forms.NumberInput(attrs={'class': 'form-control', 'min': 200}),
            'immagine_sfondo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'visibile': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



#------------------------------------------------------------------------------------------------------------------

from django import forms
from blog.models import ProdottoSuggerito

class ProdottoSuggeritoForm(forms.ModelForm):
    class Meta:
        model = ProdottoSuggerito
        fields = '__all__'
#----------------------------------------------------------------------------------------------------

from core.models import CodiceSconto
from django import forms

class CodiceScontoGeneraForm(forms.ModelForm):
    class Meta:
        model = CodiceSconto
        fields = ['codice', 'percentuale', 'attivo', 'scadenza', 'utente', 'multiuso']  # ← solo se esistono nel modello!
#------------------------------------------------------------------------------------------------------------------
