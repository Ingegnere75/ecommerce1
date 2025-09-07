

# core/forms.py

from django import forms
from .models import PaginaInformativa
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import HomeCard, HomeBanner


#----------checkout-------------------------------------------------------------------------

class CheckoutForm(forms.Form):
    nome = forms.CharField(max_length=100)
    cognome = forms.CharField(max_length=100)
    indirizzo = forms.CharField(max_length=255)
    civico = forms.CharField(max_length=10)
    cap = forms.CharField(max_length=10)
    citta = forms.CharField(max_length=100)
    provincia = forms.CharField(max_length=100)

    fatturazione_diversa = forms.BooleanField(required=False)

    indirizzo_fatturazione = forms.CharField(max_length=255, required=False)
    civico_fatturazione = forms.CharField(max_length=10, required=False)
    cap_fatturazione = forms.CharField(max_length=10, required=False)
    citta_fatturazione = forms.CharField(max_length=100, required=False)
    provincia_fatturazione = forms.CharField(max_length=100, required=False)


#-----------pagina informativa----------------------------------------------------------------------

class PaginaInformativaForm(forms.ModelForm):
    contenuto_testo = forms.CharField(widget=CKEditor5Widget(config_name='default'))

    class Meta:
        model = PaginaInformativa
        fields = '__all__'


#-------------------------------------------------------------------------------------------------------------



from .colori import COLORI_NOMI




from django import forms
from .models import Prodotto
from .widgets import ColoriPreviewWidget

class ProdottoAdminForm(forms.ModelForm):
    colorazioni = forms.CharField(
        required=False,
        widget=ColoriPreviewWidget(),
        label='Colori Disponibili',
        help_text='Clicca per selezionare o deselezionare i colori.'
    )

    class Meta:
        model = Prodotto
        fields = '__all__'

    def clean_colorazioni(self):
        data = self.cleaned_data['colorazioni']
        return ', '.join([c.strip() for c in data.split(',') if c.strip()])

#---------------------------------------------------------------------------------------------------------------

from django import forms
from decimal import Decimal
from .models import PrezzoSpedizione, Ordine

class CalcolaPrezzoForm(forms.Form):
    ordine = forms.ModelChoiceField(
        queryset=Ordine.objects.all(),
        label="Ordine",
        help_text="Seleziona l'ordine da calcolare."
    )
    prezzo_spedizione = forms.DecimalField(
        max_digits=7,
        decimal_places=2,
        required=False,
        label="Prezzo Spedizione (€)",
        initial=0,
        help_text="Inserisci il costo della spedizione (opzionale)."
    )
    percentuale_sconto = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        label="Sconto (%)",
        initial=0,
        help_text="Inserisci una percentuale di sconto (0-100)."
    )

    totale_calcolato = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Totale Finale (€)",
        disabled=True,
        initial=0,
        help_text="Il totale verrà calcolato automaticamente."
    )

    def clean(self):
        cleaned_data = super().clean()
        ordine = cleaned_data.get('ordine')
        prezzo_spedizione = cleaned_data.get('prezzo_spedizione') or Decimal('0.00')
        percentuale_sconto = cleaned_data.get('percentuale_sconto') or 0

        if ordine:
            # 1. Prendo il totale base dell'ordine
            totale = ordine.get_totale()

            # 2. Applico lo sconto
            sconto = (totale * Decimal(percentuale_sconto)) / Decimal('100')
            totale_scontato = totale - sconto

            # 3. Aggiungo la spedizione
            totale_finale = totale_scontato + prezzo_spedizione

            # 4. Imposto il totale calcolato
            cleaned_data['totale_calcolato'] = totale_finale

        return cleaned_data

from django import forms

class CodiceScontoForm(forms.Form):
    codice = forms.CharField(
        label='Codice Sconto',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
#--------------------------------------------------------------------------------------------------
from django import forms
from .models import SottoCategoria

class SottoCategoriaForm(forms.ModelForm):
    class Meta:
        model = SottoCategoria
        fields = '__all__'
        widgets = {
            'contenuto_html': forms.Textarea(attrs={'rows': 6, 'cols': 80}),
        }


