from django.urls import path
from . import views

urlpatterns = [
    path('salva-contenuto/', views.salva_contenuto, name='salva_contenuto'),
]
