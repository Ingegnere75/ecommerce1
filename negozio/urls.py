from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('admin-secure/', admin.site.urls),                # ✅ Accesso Django Admin SICURO
    path('', include('core.urls')),                        # Pagina pubblica
    path('accounts/', include('accounts.urls')),           # Area utente
    path('amministratore/', include('amministratore.urls')), # Area admin personalizzata
    #path('schema-viewer/', include('schema_viewer.urls')),
    path('contenuti/', include('contentcollector.urls')),
    path('richieste/', include('requesttracker.urls')),
    path('log/', include('logmanager.urls')),
    
    path('blog/', include('blog.urls')),


]

# Per lo sviluppo, gestiamo i file media (immagini, etc.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
