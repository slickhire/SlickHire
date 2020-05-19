from datetime import datetime
from django.utils.crypto import get_random_string
from . import models 

from django.core.mail import send_mail
from django.conf import settings

#from .integrator import CallHandler 
#from .integrator import StartQuestionaireReminder 

def email():
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['rajeshwarp2002@gmail.com',]
    send_mail( subject, message, email_from, recipient_list )

def handle_uploaded_file(f, jobId):
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H:%M:%S")
    with open('tutorial/static/upload/'+ jobId + '#' + dt_string + '_' + f.name, 'wb+') as destination:  
        for chunk in f.chunks():  
            destination.write(chunk) 
