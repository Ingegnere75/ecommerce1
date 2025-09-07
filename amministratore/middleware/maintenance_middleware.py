from django.shortcuts import render
from amministratore.models import SiteSettings
from django.urls import reverse

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            settings = SiteSettings.objects.first()
            if settings and settings.maintenance_mode:
                if not request.user.is_authenticated or not request.user.is_staff:
                    if not request.path.startswith('/admin/') and not request.path.startswith(reverse('admin_login')):
                        return render(request, 'amministratore/maintenance.html', status=503)
        except:
            pass
        return self.get_response(request)
