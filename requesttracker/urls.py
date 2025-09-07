from django.urls import path
from . import views

urlpatterns = [
    path('salva-richiesta/', views.salva_richiesta, name='salva_richiesta'),
]
