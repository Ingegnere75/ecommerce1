from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    login_view, logout_view, register_view, invia_reclamo, ticket_view,
     miei_ordini
)
from amministratore.views import toggle_stato_ticket, elimina_ticket
from .views import register_view, confirm_otp

urlpatterns = [
    # ✅ Autenticazione base-----------------------------------------------------------------------
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('confirm-otp/', confirm_otp, name='confirm_otp'),
    # ❤️ Wishlist----------------------------------------------------------------------------------------------
    path('wishlist/toggle/<int:prodotto_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.mia_wishlist, name='mia_wishlist'),
    path('wishlist/remove/<int:prodotto_id>/', views.rimuovi_dalla_wishlist, name='rimuovi_dalla_wishlist'),
    path('wishlist/add_to_cart/<int:prodotto_id>/', views.aggiungi_dalla_wishlist_al_carrello, name='aggiungi_dalla_wishlist_al_carrello'),

    # 🍪 Gestione Cookie----------------------------------------------------------------------------------------------
    path('i-tuoi-cookie/', views.cookie_user_view, name='cookie_user'),
    path('elimina-cookie-user/<int:cookie_id>/', views.elimina_cookie_user, name='elimina_cookie_user'),
    path('cookies/elimina-tutti/', views.elimina_tutti_cookie_user, name='elimina_tutti_cookie_user'),

    # 🔐 Recupero password (Password Reset Flow)-------------------------------------------------------------------------
    path('password_reset_request/', views.password_reset_request, name='password_reset_request'),
    path('password_reset_verify/', views.password_reset_verify, name='password_reset_verify'),
    path('password_reset_new_password/', views.password_reset_new_password, name='password_reset_new_password'),
    # 👤 Dashboard e profilo------------------------------------------------------------------------------------------
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profilo/', views.profilo, name='profilo'),
    path('ordini/', views.ordini, name='ordini'),

    # 🧾 Reclami e ticket----------------------------------------------------------------------------------------------
    path('reclami/', invia_reclamo, name='reclami'),
    path('ticket/', ticket_view, name='ticket'),
    path('ticket/<int:ticket_id>/toggle/', toggle_stato_ticket, name='toggle_stato_ticket'),
    path('ticket/<int:ticket_id>/elimina/', elimina_ticket, name='elimina_ticket'),

    # 📦 Ordini utente--------------------------------------------------------------------------------------------------
    path('i-miei-ordini/', miei_ordini, name='miei_ordini'),
    path('esporta-ordine/<int:ordine_id>/', views.esporta_ordine_pdf, name='esporta_ordine'),
    path('consulta-reclami/', views.consulta_reclami, name='consulta_reclami'),
    path('riordina/<int:ordine_id>/', views.riordina_ordine, name='riordina_ordine'),

    # 🔑 Cambio password utente loggato-------------------------------------------------------------------------------------
    path('cambio-password/',
         auth_views.PasswordChangeView.as_view(
             template_name='accounts/change_password.html',
             success_url=reverse_lazy('dashboard')
         ),
         name='cambio_password'),
     path('sconti/', views.lista_sconti, name='lista_sconti'),
    #----------------------------------------------------------------------------------------------------------------------------     
]
