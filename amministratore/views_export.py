# amministratore/views_export.py
import openpyxl
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from contentcollector.models import ContentText
from requesttracker.models import UserRequest
from logmanager.models import LogEntry

def export_dashboard_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Dashboard Dati"

    ws.append(['Sezione', 'Conteggio'])
    ws.append(['Contenuti', ContentText.objects.count()])
    ws.append(['Richieste', UserRequest.objects.count()])
    ws.append(['Log', LogEntry.objects.count()])
    # Non mettiamo più Pagine!

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=dashboard_dati.xlsx'
    wb.save(response)
    return response

def export_dashboard_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=dashboard_dati.pdf'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 18)
    p.drawString(200, height - 50, "Dashboard Report")

    p.setFont("Helvetica", 14)
    y = height - 100

    p.drawString(100, y, f"Contenuti Raccolti: {ContentText.objects.count()}")
    y -= 30
    p.drawString(100, y, f"Richieste Raccolte: {UserRequest.objects.count()}")
    y -= 30
    p.drawString(100, y, f"Log Registrati: {LogEntry.objects.count()}")
    # Non mettiamo più Pagine!

    p.showPage()
    p.save()
    return response
