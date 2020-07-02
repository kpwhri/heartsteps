from import_export import resources
from import_export.fields import Field
from import_export.admin import ExportMixin

from .models import MorningMessage

class MorningMessageResource(resources.ModelResource):

    class Meta:
        model = MorningMessage
        fields = ('date', 'notification', 'anchor')
