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

def handle_uploaded_file(f):
    models.Questions.objects.all().delete()
    q = models.Questions(key="qa", q="What is expected ctc", options = "", tagId = "expectedCtc", expected1 = "5", expected2 = "7")
    q.save()
    q = models.Questions(key="qa", q="What is your current company name", options = "", tagId = "company")
    q.save();
    q = models.Questions(key="qa", q="How much is your experience in years", options = "", tagId = "experience", expected1 = "5", expected2 = "7")
    q.save()

    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H:%M:%S")
    with open('tutorial/static/upload/'+ dt_string + '_' + f.name, 'wb+') as destination:  
        for chunk in f.chunks():  
            destination.write(chunk) 

    #CallHandler()
    #StartQuestionaireReminder()

    #p = models.Person(name="xyz", mobile="888", stringId = get_random_string(length=30), questions = "qa")
    #p.save()
    #p = models.Person(name="iaxyz", mobile="9888", stringId = get_random_string(length=30), questions = "qa")
    #p.save()
