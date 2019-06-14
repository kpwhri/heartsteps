from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SendSMSForm
from .models import SendSMS
from .utils import send_twilio_message


class SendSmsCreateView(SuccessMessageMixin, CreateView):
    form_class = SendSMSForm
    http_method_names = ('post', )
    success_message = 'SMS successfully sent'
    success_url = reverse_lazy('dashboard-index')
    template_name = 'sms_service/sendsms_form.html'

    # Rerouting the post from the modal form in dashboard
    # isn't automatically running form_valid.
    def post(self, request, *args, **kwargs):
        print("Am i really posting?")
        form = self.form_class(request.POST)
        return self.form_valid(form)

    def form_valid(self, form):
        for error in form.errors:
            print("Error in " + error)
        # save message and ancillary info
        SendSMSForm.process_sms_message(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(self)

