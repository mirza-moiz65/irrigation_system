# from io import BytesIO
# from django.http import HttpResponse
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas

# def generate_report(ranch):
#     buffer = BytesIO()
#     p = canvas.Canvas(buffer, pagesize=letter)
#     p.drawString(100, 750, f"Irrigation Schedule for Ranch: {ranch.name}")
#     # Add more details to the PDF
#     p.showPage()
#     p.save()
#     buffer.seek(0)
#     return buffer

# def download_report(request, ranch_id):
#     ranch = Ranch.objects.get(id=ranch_id)
#     buffer = generate_report(ranch)
#     return HttpResponse(buffer, as_attachment=True, content_type='application/pdf')
