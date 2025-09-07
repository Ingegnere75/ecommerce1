from django.urls import path
from django.views.generic import TemplateView
from . import views
from core.views import (
    checkout, riepilogo_ordine, scelta_pagamento,
    stripe_checkout, paypal_checkout, scalapay_checkout,
    successo, applica_sconto_view
)
from amministratore.views import lista_cookie
from .views import check_session
from . import views
from .views import elimina_codici_scaduti_admin
urlpatterns = [
    #------ HOME E GENERALI -------------------------------------------------------------------
    path('', views.home, name='home'),
    path('editor-home/', views.editor_home, name='editor_home'),
    path('admin/editor-visuale/', views.editor_visuale, name='editor_visuale'),
    path('salva-layout/', views.salva_layout, name='salva_layout'),
    path("salva-cookie-consent/", views.salva_cookie_consent, name="salva_cookie_consent"),
    path('carrello/sconto/', applica_sconto_view, name='applica_sconto'),
    path('spese/', lista_cookie, name='lista_cookie'),
    path('check-session/', check_session, name='check_session'),
    path('admin/elimina_codici_scaduti/', views.elimina_codici_scaduti_admin, name='elimina_codici_scaduti_admin'),
    path('admin/elimina-codici-sconto/', elimina_codici_scaduti_admin, name='elimina_codici_sconto_admin'),
    #------ PAGINE STATICHE -------------------------------------------------------------------
    path('chi-siamo/', TemplateView.as_view(template_name="core/chi_siamo.html"), name='chi_siamo'),
    path('sostenibilita/', TemplateView.as_view(template_name="core/sostenibilita.html"), name='sostenibilita'),
    path('faq/', TemplateView.as_view(template_name="core/faq.html"), name='faq'),
    path('spedizione/', TemplateView.as_view(template_name="core/spedizione.html"), name='spedizione'),
    path('resi/', TemplateView.as_view(template_name="core/resi.html"), name='resi'),
    path('termini-condizioni/', TemplateView.as_view(template_name="core/termini_condizioni.html"), name='termini_condizioni'),
    path('trattamento-dati/', TemplateView.as_view(template_name="core/trattamento_dati.html"), name='trattamento_dati'),
    path('informativa-privacy/', TemplateView.as_view(template_name="core/informativa_privacy.html"), name='informativa_privacy'),
    path('privacy/', TemplateView.as_view(template_name="core/privacy.html"), name='privacy'),
    path('cookie/', TemplateView.as_view(template_name="core/cookie.html"), name='cookie'),
    path('pagamenti/', TemplateView.as_view(template_name="core/pagamenti.html"), name='pagamenti'),

    #------ PAGINE DINAMICHE ------------------------------------------------------------------
    path('pagine/<slug:slug>/', views.pagina_dinamica, name='pagina_dinamica'),

    #------ PRODOTTI & CATEGORIE --------------------------------------------------------------
    path('prodotti/', views.prodotti, name='prodotti'),
    path('categorie/', views.categorie, name='categorie'),
    path('categoria/<slug:slug>/', views.dettaglio_categoria, name='dettaglio_categoria'),
    path('prodotti-per-categoria/<slug:slug>/', views.prodotti_per_categoria, name='prodotti_per_categoria'),
    path('prodotti/sottocategoria/<slug:slug>/', views.prodotti_per_sottocategoria, name='prodotti_per_sottocategoria'),
    path('ajax/sottocategorie/<int:categoria_id>/', views.sottocategorie_ajax, name='ajax_sottocategorie'),
    path('prodotto/<int:pk>/', views.dettaglio_prodotto_by_id, name='dettaglio_prodotto'),

    #------ CARRELLO & CHECKOUT ---------------------------------------------------------------
    path('carrello/', views.carrello, name='carrello'),
    path('aggiungi-al-carrello/<int:prodotto_id>/', views.aggiungi_al_carrello, name='aggiungi_al_carrello'),
    path('carrello/aggiorna/<int:item_id>/', views.aggiorna_quantita, name='aggiorna_quantita'),
    path('carrello/rimuovi/<int:item_id>/', views.rimuovi_dal_carrello, name='rimuovi_dal_carrello'),
    path('checkout/', checkout, name='checkout'),
    path('riepilogo-ordine/', riepilogo_ordine, name='riepilogo_ordine'),
    path('scegli-pagamento/', scelta_pagamento, name='scegli_pagamento'),
    path('stripe-checkout/', stripe_checkout, name='stripe_checkout'),
    path('paypal-checkout/', paypal_checkout, name='paypal_checkout'),
    path('scalapay-checkout/', scalapay_checkout, name='scalapay_checkout'),
    path('successo/', successo, name='successo'),
    path('pagamento-completato/', views.paypal_success, name='paypal_success'),

    #------ ORDINI -----------------------------------------------------------------------------
    path('ordini/', views.ordini, name='ordini'),
    
    path('ordine-completato/', views.ordine_completato, name='ordine_completato'),

    #------ ALTRE FUNZIONI ---------------------------------------------------------------------
    path('ricerca/', views.ricerca_view, name='ricerca'),
    path('paypal/payment/', views.paypal_payment, name='paypal_payment'),
    path('contatti/', views.contatti, name='contatti'),
    path('wishlist/', views.wishlist, name='wishlist'),

    path('stripe-checkout/', views.stripe_checkout, name='stripe_checkout'),
    path('annulla-pagamento/', views.annulla_pagamento, name='annulla_pagamento'),
    
    


]
