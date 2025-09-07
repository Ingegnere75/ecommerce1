from django.urls import path
from . import views

urlpatterns = [
    path('salva-log/', views.salva_log, name='salva_log'),
]
