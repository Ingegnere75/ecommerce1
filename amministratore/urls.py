from django.urls import path
from . import views
from .views import magazzino_entrate
from .views import lista_ordini
from .forms import PrezzoSpedizioneForm, CodiceScontoGeneraForm
from .views import gestione_spese_e_sconti
from django.urls import path
from amministratore import views as amministratore_views
from amministratore import views_export as views_export
from core import views as core_views  # solo se ti serve la dashboard utente normale
from core import views as core_views
from .views import admin_login_view
from amministratore import views_export 
from django.urls import path
from .views import lista_strisce_info, aggiungi_striscia, modifica_striscia, elimina_striscia
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from core.models import OrdineItem
from .views import elimina_uscita_magazzino
from core.models import Ordine
from amministratore.views import test_email_smtp
from .views import elimina_ordine_non_pagato

from .views import situazione_magazzino
from .views import esporta_magazzino_pdf
from .views import modifica_entrata_magazzino
from .views import elimina_entrata_magazzino
from .views import get_prodotto_info
urlpatterns = [
    # Dashboard e profilo
    path('dashboard/', views.dashboard, name='admin-dashboard'),
    #------------categorie---------------------------------------------------------------------------------------
    path('categorie/', views.categorie_list, name='categorie_list'),
    path('categorie/aggiungi/', views.aggiungi_categoria, name='aggiungi_categoria'),
    path('categorie/modifica/<int:id>/', views.modifica_categoria, name='modifica_categoria'),
    path('categorie/elimina/<int:id>/', views.elimina_categoria, name='elimina_categoria'),
    path('gestione-spese-sconti/', gestione_spese_e_sconti, name='gestione_spese_sconti'),
    #-----------------sottocategorie--------------------------------------------------------------------------------
   
    path('admin/sottocategorie/', views.sottocategorie_admin_view, name='admin-sottocategoria'),
    path('admin/sottocategorie/aggiungi/', views.aggiungi_sottocategoria, name='aggiungi_sottocategoria'),
    path('admin/sottocategorie/modifica/<int:id>/', views.modifica_sottocategoria, name='modifica_sottocategoria'),
    path('admin/sottocategorie/elimina/<int:id>/', views.elimina_sottocategoria, name='elimina_sottocategoria'),
    path('cookie/', views.lista_cookie, name='lista_cookie'),
    path('cookie/delete/<int:pk>/', views.elimina_cookie, name='elimina_cookie'),
    #----------- dati negozio ------------------------------------------------------------------------------ 
    path('dati-negozio/', views.dati_negozio_admin_view, name='dati_negozio_admin'),
    path('dati-negozio/modifica/', views.modifica_dati_negozio, name='modifica_dati_negozio'),
    path('dati-negozio/elimina/<int:id>/', views.elimina_dati_negozio, name='elimina_dati_negozio'),
    path('dati-negozio/usa/<int:id>/', views.usa_dati_negozio, name='usa_dati_negozio'),
    #------------------------------------------------------------------------------------------------------
    path('magazzino/entrata/modifica/<int:pk>/', views.modifica_entrata_magazzino, name='modifica_entrata_magazzino'),
    path('magazzino/entrata/elimina/<int:pk>/', views.elimina_entrata_magazzino, name='elimina_entrata_magazzino'),
    # Ordini----------------------------------------------------------------------------------------------------------
    path('ordini/', views.lista_ordini, name='ordini'), 
    path('ordini/', views.lista_ordini, name='admin-ordini'), 
    path('amministratore/ordini/', lista_ordini, name='lista_ordini'),
    path('admin/ordini/<int:ordine_id>/elimina/', elimina_ordine_non_pagato, name='elimina_ordine_non_pagato'),
    #brand-----------------------------------------------------------------------------------------------------
    path('admin-secure/brand/<int:id>/', views.vedi_brand, name='vedi_brand'),
    path('admin-secure/brand/<int:id>/modifica/', views.modifica_brand, name='modifica_brand'),
    #profilo-------------------------------------------------------------------------------------------------------------
    path('profilo/', views.lista_utenti, name='admin-profilo'),
    path('profilo/', views.lista_utenti, name='lista_utenti'),
    path('profilo/modifica/<int:id>/', views.modifica_utente_ajax, name='modifica_utente_ajax'),
    path('profilo/elimina/<int:id>/', views.elimina_utente, name='elimina_utente'),
    #ordini-----------------------------------------------------------------------------------------------------------------------
    path('ordini/pdf/<int:ordine_id>/', views.esporta_ordine_pdf, name='esporta_ordine'),
    path('utenti/ordini/<int:ordine_id>/', views.dettaglio_utente_ordini, name='dettaglio_utente_ordini'),
    path('ordini/elimina/<int:ordine_id>/', views.elimina_ordine, name='elimina_ordine'),
    # Magazzino---------------------------------------------------------------------------------------------------------------------
    path('magazzino/', views.magazzino, name='admin-magazzino'),




    path('admin/situazione-magazzino/', situazione_magazzino, name='situazione_magazzino'),
    path('admin/esporta-magazzino/', esporta_magazzino_pdf, name='esporta_magazzino_pdf'),




    path('magazzino/aggiungi/', views.aggiungi_prodotto, name='aggiungi_prodotto'),
    path('magazzino/modifica/<int:pk>/', views.modifica_prodotto, name='modifica_prodotto'),
    path('magazzino/elimina/<int:pk>/', views.elimina_prodotto, name='elimina_prodotto'),
    
    path('magazzino/entrate/toggle-aggiunto/<int:pk>/', views.toggle_aggiunto, name='toggle_aggiunto'),

    path('admin/magazzino/entrate/', magazzino_entrate, name='magazzino_entrate'),
    path('admin/magazzino/entrata/<int:pk>/modifica/', modifica_entrata_magazzino, name='modifica_entrata_magazzino'),
    path('admin/magazzino/entrata/<int:pk>/elimina/', elimina_entrata_magazzino, name='elimina_entrata_magazzino'),
    path('amministratore/get_prodotto_info/', get_prodotto_info, name='get_prodotto_info'),


    path('magazzino/uscite/', views.magazzino_uscite, name='magazzino_uscite'),
    
    path('magazzino/uscite/elimina/<int:id>/', elimina_uscita_magazzino, name='elimina_uscita_magazzino'),
    path('statistiche/', views.statistiche, name='admin-statistiche'),
   
    # Pagine dinamiche------------------------------------------------------------------------------------------------------------------------
    path('pagine/', views.lista_pagine, name='lista_pagine'),
    path('pagine/aggiungi/', views.aggiungi_pagina, name='aggiungi_pagina'),
    path('pagine/modifica/<slug:slug>/', views.modifica_pagina, name='modifica_pagina'),
    path('pagine/rimuovi/<slug:slug>/', views.rimuovi_pagina, name='rimuovi_pagina'),
    path('pagine/<slug:slug>/', views.pagina_dinamica, name='pagina_dinamica'),
    
    # Ticket----------------------------------------------------------------------------------------------------
    path('reclami/', views.gestione_reclami, name='gestione_reclami'),
    path('reclami/<int:id>/', views.dettaglio_reclamo, name='dettaglio_reclamo'),
    path('reclami/<int:id>/rispondi/', views.rispondi_reclamo, name='rispondi_reclamo'),
   
    # Admin Django redirect------------------------------------------------------------------------------------------------------------------------------
    path('admin-django/', views.redirect_admin_django, name='admin-django'),

    # Messaggi----------------------------------------------------------------------------------------------------------------------------------------------------
    path('admin-messaggi/', views.admin_messaggi, name='admin-messaggi'),
    path('rispondi-messaggio/<int:id>/', views.rispondi_messaggio, name='rispondi_messaggio'),
    path('admin-rispondi/<int:messaggio_id>/', views.admin_rispondi, name='admin-rispondi'),
    path('admin-elimina-messaggio/<int:messaggio_id>/', views.admin_elimina_messaggio, name='admin-elimina-messaggio'),
    #---gestione home -------------------------------------------------------------------------------------------------------------------------------------------------------------
    path('modifica-card/<int:card_id>/', views.modifica_card, name='modifica_card'),
    path('modifica-banner/<int:banner_id>/', views.modifica_banner, name='modifica_banner'),
    path('gestione-home/', views.gestione_home, name='gestione_home'),
    path('gestione-home/', views.gestione_home, name='gestione_home'),
    path('aggiungi-card/', views.aggiungi_card, name='aggiungi_card'),
    path('elimina-card/<int:card_id>/', views.elimina_card, name='elimina_card'),


    path('aggiungi-banner/', views.aggiungi_banner, name='aggiungi_banner'),
    path('elimina-banner/<int:banner_id>/', views.elimina_banner, name='elimina_banner'),
    path('elementi/aggiungi/', views.aggiungi_elemento, name='aggiungi_elemento'),
    path('elementi/modifica/<int:elemento_id>/', views.modifica_elemento, name='modifica_elemento'),
    path('elementi/elimina/<int:elemento_id>/', views.elimina_elemento, name='elimina_elemento'),

    path('gestione-pagamenti/', views.gestione_pagamenti, name='gestione_pagamenti'),
   
#-----------------------------------------------------------------------------------------------------------------

    
    # Dashboard amministratore
    path('dashboard/', core_views.dashboard, name='admin-dashboard'),  # Se è nel core
    
    # Dashboard dati e dashboard globale (admin)--------------------------------------------------------------------------
    path('dashboard-dati/', amministratore_views.dati_home, name='dashboard-dati'),
    path('dashboard-globale/', amministratore_views.dashboard_globale, name='dashboard-globale'),

    # Export Excel e PDF----------------------------------------------------------------------------------------------
    path('dashboard-globale/export-excel/', views_export.export_dashboard_excel, name='dashboard-export-excel'),
    path('dashboard-globale/export-pdf/', views_export.export_dashboard_pdf, name='dashboard-export-pdf'),

    # Gestione Contenuti-------------------------------------------------------------------------------------------
    path('contenuti-lista/', views.contenuti_lista, name='contenuti-lista'),
    path('contenuti-add/', views.contenuti_add, name='contenuti-add'),
    path('contenuti-modifica/<str:pk>/', views.contenuti_modifica, name='contenuti-modifica'),
    path('contenuti-elimina/<str:pk>/', views.contenuti_elimina, name='contenuti-elimina'),

    path('richieste-lista/', views.richieste_lista, name='richieste-lista'),
    path('richieste-add/', views.richieste_add, name='richieste-add'),
    path('richieste-modifica/<str:pk>/', views.richieste_modifica, name='richieste-modifica'),
    path('richieste-elimina/<str:pk>/', views.richieste_elimina, name='richieste-elimina'),
    # Gestione Log-----------------------------------------------------------------------------------------------
    path('log-lista/', amministratore_views.log_lista, name='log-lista'),
    path('controllo-contenuti/', amministratore_views.dashboard_contenuti_mongo, name='controllo-contenuti'),
    path('amministratore/dashboard-ai/', amministratore_views.dashboard_ai_admin, name='admin-statistiche'),
    #-------------------------------------------------------------------------------------------------------------
    path('toggle-maintenance/', views.toggle_maintenance, name='toggle_maintenance'),
    path('admin-login/', admin_login_view, name='admin_login'),

   #-----------------------------------------------------------------------------------------------------
     
    path('strisce-info/', lista_strisce_info, name='lista_strisce_info'),
    path('strisce-info/aggiungi/', aggiungi_striscia, name='aggiungi_striscia'),
    path('strisce-info/modifica/<int:pk>/', modifica_striscia, name='modifica_striscia'),
    path('strisce-info/elimina/<int:pk>/', elimina_striscia, name='elimina_striscia'),

#-----------blog------------------------------------------------------------------------------------------



#---------------------------------------------------------------------------------------------------------------

    path('gestore/', views.gestore_blog, name='gestore-blog'),

# Articoli Blog-----------------------------------------------------------------------------------------------
    path('gestore/articoli/', views.gestione_articoli_blog, name='admin-articoli-blog'),
    path('gestore/articoli/add/', views.articoli_blog_add, name='admin-articoli-blog-add'),
    path('gestore/articoli/<int:pk>/edit/', views.articoli_blog_edit, name='admin-articoli-blog-edit'),
    path('gestore/articoli/<int:pk>/delete/', views.articoli_blog_delete, name='admin-articoli-blog-delete'),
    
# Commenti Blog-------------------------------------------------------------------------------------------------
    path('gestore/commenti/', views.gestione_commenti_blog, name='admin-commenti-blog'),
    path('gestore/commenti/elimina/<int:id>/', views.elimina_commento_blog, name='elimina-commento-blog'),

# Prodotti Suggeriti------------------------------------------------------------------------------------------
    path('gestore/prodotti/', views.gestione_prodotti_blog, name='admin-prodotti-blog'),

# Banner---------------------------------------------------------------------------------------------------------
    path('gestore/banner/', views.gestione_banner_blog, name='admin-banner-blog'),
    path('gestore/banner/add/', views.banner_blog_add, name='admin-banner-blog-add'),
    path('gestore/banner/add/', views.banner_blog_add, name='admin-banner-blog-add'),
    path('gestore/banner/<int:pk>/edit/', views.banner_blog_edit, name='admin-banner-blog-edit'),
    path('gestore/banner/<int:pk>/delete/', views.banner_blog_delete, name='admin-banner-blog-delete'),
    path('gestore/prodotti/add/', views.aggiungi_prodotto_suggerito, name='admin-prodotti-blog-add'),
    path('test-email/', test_email_smtp, name='test_email_smtp'),

]



    




