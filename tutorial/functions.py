from datetime import datetime
from django.utils.crypto import get_random_string
from . import models 

from django.core.mail import send_mail
from django.conf import settings

from multiprocessing import Process

from .integrator import ResumeHandler 
from .integrator import StartQuestionaireReminder 
from .integrator import OnlineTestEval 

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
	r = models.OnlineTestKeys(qid=1, type=1, question="Who invented computers?", choice1="Anthony", choice2="Rama", choice3="Kempa", choice4="Charles", answer="Charles")
	r.save()
	r = models.OnlineTestKeys(qid=2, type=1, question="Which of the below are binary operators?", choice1="&", choice2="|", choice3="||", choice4="~", answer="||")
	r.save()
	r = models.OnlineTestKeys(qid=3, type=1, question="Which of these protocols are layer4 protocols?", choice1="TCP", choice2="ARP", choice3="IP", choice4="ICMP", answer="TCP")
	r.save()
	r = models.OnlineTestKeys(qid=4, type=0, question="Write a sample program to add two numbers?", test1="2 3;5", test2="-1 -5;-6", test3="-1 5;4", test4="200 900;1100", test5="0 -1;-1")
	r.save()
	r = models.OnlineTestKeys(qid=5, type=0, question="Write a sample program to find out whether the year is a leap year?", test1="2000;Yes", test2="2020;Yes", test3="4;Yes", test4="2025;No", test5="1998;No")
	r.save()
	print("Ganga All questions created")

def StartProcesses():
	o = Process(target=OnlineTestEval)
	o.start()

	q = Process(target=StartQuestionaireReminder)
	q.start()

	p = Process(target=ResumeHandler)
	p.start()
