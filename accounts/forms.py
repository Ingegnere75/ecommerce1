from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    PasswordChangeForm, PasswordResetForm, SetPasswordForm
)
from accounts.models import UserProfile 
from .models import Reclamo

#-----------------------------------------------------------------------------------------------------------------------
# 🔐 REGISTRAZIONE
class UserRegisterForm(forms.Form):
    nome = forms.CharField(label='Nome', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    cognome = forms.CharField(label='Cognome', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    indirizzo = forms.CharField(label='Indirizzo', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    civico = forms.CharField(label='Civico', max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    cap = forms.CharField(label='CAP', max_length=5, widget=forms.TextInput(attrs={'class': 'form-control'}))
    citta = forms.CharField(label='Città', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    provincia = forms.CharField(label='Provincia', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    codice_fiscale = forms.CharField(label='Codice Fiscale', max_length=16, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(label='Telefono', max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))

    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Ripeti Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError("❌ Le password non coincidono.")

        return cleaned_data

#---------------------------------------------------------------------------------------------------------------------
# 🛠️ MODIFICA PROFILO
class ModificaProfiloForm(forms.ModelForm):
    email = forms.EmailField(disabled=True, label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['nome', 'cognome', 'indirizzo', 'civico', 'cap', 'citta', 'provincia', 'codice_fiscale', 'telefono']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cognome': forms.TextInput(attrs={'class': 'form-control'}),
            'indirizzo': forms.TextInput(attrs={'class': 'form-control'}),
            'civico': forms.TextInput(attrs={'class': 'form-control'}),
            'cap': forms.TextInput(attrs={'class': 'form-control'}),
            'citta': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'codice_fiscale': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email

#-------------------------------------------------------------------------------------------------------------------
# 📩 RECUPERO PASSWORD
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label='Inserisci la tua email', max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'}))

#-------------------------------------------------------------------------------------------------------------------
# 🔄 NUOVA PASSWORD dopo reset
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Nuova Password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label="Conferma nuova Password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )

#---------------------------------------------------------------------------------------------------------------
# 🔒 CAMBIO PASSWORD da loggato
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Vecchia Password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label="Nuova Password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label="Conferma Nuova Password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )

#------------------------------------------------------------------------------------------------------------------
# 📬 RECLAMO
class ReclamoForm(forms.ModelForm):
    class Meta:
        model = Reclamo
        fields = ['nome', 'cognome', 'email', 'oggetto', 'messaggio', 'allegato']  # 👈 Rimosso numero_ordine
        labels = {
            'nome': 'Nome',
            'cognome': 'Cognome',
            'email': 'Email',
            'oggetto': 'Oggetto del Reclamo',
            'messaggio': 'Messaggio',
            'allegato': 'Allegato (immagine/video opzionale)',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cognome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'oggetto': forms.TextInput(attrs={'class': 'form-control'}),
            'messaggio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'allegato': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        self.fields['allegato'].required = False

#-------------------------------------------------------------------------------------------------------------
