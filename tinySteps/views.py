from django.shortcuts import render, redirect, get_object_or_404
from .models import InfoRequestModel
from .forms import InfoRequestForm
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string

# #########################################################################
# VIEWS FOR FUNCTION-BASED VIEWS
# #########################################################################
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')


# #########################################################################
# VIEWS FOR CLASS-BASED VIEWS
# #########################################################################
class InfoRequestCreate(SuccessMessageMixin, generic.CreateView):
    template_name = 'info_request_create.html'
    model = InfoRequestModel
    form_class = InfoRequestForm
    success_message = "Thank you, %(name)s! Your request has been sent successfully. Check your email for more information!"

    # ENVIAR CORREO ELECTRONICO AL USUARIO, SI EL FORM ES VALIDO
    def form_valid(self, form):
        response = super().form_valid(form)
        # ENVIAMOS EL CORREO ELECTRONICO
        info_request = form.instance
        subject = 'Info Request Received'
        message = render_to_string('info_request_email.txt', {
            'name': info_request.name,
        })
        send_mail(
            subject,
            message,
            'c4relecloud@gmail.com',
            [info_request.email],
            fail_silently=False,
        )
        return response
