from django.urls import path
from . import views

urlpatterns = [
    # Sezioni admin
    path('dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('magazzino/', views.magazzino_admin, name='magazzino_admin'),
    path('spedizioni/', views.spedizioni_admin, name='spedizioni_admin'),
    path('statistiche/', views.statistiche_admin, name='statistiche_admin'),
    path('contatti/', views.contatti_admin, name='contatti_admin'),

    # Editor visuale
    path('editor-home/', views.editor_home, name='editor_home'),
    path('importa-home/', views.importa_home, name='importa_home'),
    path('salva-layout/', views.salva_layout, name='salva_layout'),
    path('exporta-home-html/', views.exporta_home_html, name='exporta_home_html'),
]
