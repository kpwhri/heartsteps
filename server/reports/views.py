from django.shortcuts import render

# Create your views here.
import io
import datetime
from django.http import FileResponse

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.doctemplate import BaseDocTemplate
from reportlab.platypus.tables import Table
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch




from django.views.generic import View

class DownloadReportView(View):
    def get(self, request, *args, **kwargs):
        filename = self.get_filename("dev")

        styles = getSampleStyleSheet()
        
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(buffer)
        Story = []
        
        
        Story.append(Paragraph("<h1>Daily Report</h1>", styles["Title"]))
        Story.append(Paragraph("<h2>Study Architecture</h2>"))
        Story.append(Paragraph("<h2>Studies</h2>"))
        Story.append(Paragraph("<ul><li>Test Study 1</li><li>Test Study 2</li></ul>", styles["Bullet"]))
        Story.append(Paragraph("Sample Text."))
        
        data = [['00', '01', '02'],
                ['10', '11', '12'],
                ['20', '21', '22']]
        
        t = Table(data)
        Story.append(t)
        
        doc.build(Story)
        buffer.seek(0)
        
        return FileResponse(buffer, as_attachment=True, filename=filename)

    def get_filename(self, suffix):
        filetime = datetime.datetime.now()
        timestr = filetime.strftime("%Y%m%d-%H%M%S")
        filename = "{}_{}.pdf".format(suffix, timestr)
        return filename