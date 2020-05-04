# Notifier example from tutorial
#
# See: http://github.com/seb-m/pyinotify/wiki/Tutorial
#
'''
import pyinotify
from zipfile import ZipFile
import os 
import time
import sys
sys.path.insert(1, '/home/ubuntu/ResumeParser/resume_parser/resume_parser')
import resume_parser
from django.utils.crypto import get_random_string

from . import models
#import models
from background_task import background
from django.contrib.auth.models import User
from twilio.rest import Client

#email import starts
from django.contrib.auth.models import User

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail,EmailMessage
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.template import Context
#email import ends

wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CREATE  # watched events
"""
        self.__details = {
            'name'              : None,
            'email'             : None,
            'mobile_number'     : None,
            'skills'            : None,
            'education'         : None,
            'experience'        : None,
            'competencies'      : None,
            'measurable_results': None
        }
"""
ACCOUNT_SID = "ACbe9ca3f562c7d7fe80fc560db69fa588"
AUTH_TOKEN = "9a8ffae380118f71a6e693956c34a4b5"
SMS_NUMBER = "+18125788368"
MESSAGING_SERVICE_ID = "MG5eb6a2e338a34fa801960c2a827522d3"
#url = ec2-3-17-12-192.us-east-2.compute.amazonaws.com/questions?id=78WBofGQAosaqRAAD3MEpkZbSdALq5
#id is unique user i
def sendSMS(mobilenumber,message,url):
	print("kempa her",mobilenumber)
	client = Client(ACCOUNT_SID, AUTH_TOKEN)
	message = client.messages \
	.create(
         body="message from www.slickhire.in and click to submit the info " + url,
         messaging_service_sid=MESSAGING_SERVICE_ID,
         to=mobilenumber
     )
	print(message)

def makeVoiceCall(mobilenumber,message):
	print("kempa heer",mobilenumber)
	client = Client(ACCOUNT_SID, AUTH_TOKEN)
	call = client.calls.create(
        #twiml='<Response><Play>http://demo.rickyrobinett.com/jiggy.mp3</Play></Response>',
        url='https://handler.twilio.com/twiml/EHf4053f6f0d0778cc93de166e1856f7c3',
                        to=mobilenumber,
                        from_=SMS_NUMBER
                    )
	print(call)


def send_email(candidate_name,
          job_title,
          company_name,
          location,
          com_link,
          desc_link,
          input_link,
          optout_link,
          to_mail
          ):
    send_mail(
    'Job Alert SlickHire',
    get_template('email.html').render(
        {
            'candidate_name': candidate_name,
            'job_title': job_title,
            'company_name': company_name,
            'location': location,
            'com_link': com_link,
            'desc_link': desc_link,
            'input_link': input_link,
	    'optout_link': optout_link
        }
    ),
    settings.EMAIL_HOST_USER,
    [to_mail],
    fail_silently = False)


def AddPerson(rparser):
	print("latest",rparser['name'],rparser['email'],rparser['mobile_number'])
	p = models.Person(name=rparser['name'], mobile=rparser['mobile_number'], stringId = get_random_string(length=30), questions = "qa",email=rparser['email']
					,skills=rparser['skills'],status="pending",score=0,education=rparser['education'],experience=rparser['experience'], reminderscount=0)
	#p.save()
	id = "ec2-3-17-12-192.us-east-2.compute.amazonaws.com/questions?id=" + p.stringId
	optout_link = 'ec2-3-17-12-192.us-east-2.compute.amazonaws.com/opt_out?id=' + p.stringId
	print("kempa heer sms")
	sendSMS("+919742437310","xyz",id)
	print("kempa heer call")
	makeVoiceCall("+919742437310","kempa")
	print("kempa heer save")
	send_email(rparser['name'],"Devloper","Moto Rockr","Dharwad","www.SlickHire.in","www.SlickHire.in/jobs",id, optout_link, "anthony_1087@yahoo.com")
	p.save()

def Extarct_Files(newFile):
	print('Extract single file from ZIP')
	with ZipFile(newFile, 'r') as zipObj:
		listOfFileNames = zipObj.namelist()
		for fileName in listOfFileNames:
			zipObj.extract(fileName)
			print('Processing the new file',fileName)
			parser = resume_parser.ResumeParser(fileName)
			AddPerson(parser.get_extracted_data())

class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self, event):
		fileType = os.path.splitext(event.pathname)[-1].lower()
		print("Received created event file and type." ,event.pathname)
		if fileType == ".zip":
			#issue is event is created when the new file is created we need
			#till complete upload is done. hence adding the delay
			time.sleep(5)
			Extarct_Files(event.pathname)
		else:
			print("Unknown file Type Return Error")

@background(schedule=2)
def CallHandler():
	handler = EventHandler()
	notifier = pyinotify.Notifier(wm, handler)
	wdd = wm.add_watch('/home/ubuntu/slick_hire/tutorial/static/upload/', mask, rec=True)
	print("Watching for new file")
	notifier.loop()

import time
from datetime import datetime

def isReminderAllowedAtThisTime():
    now = datetime.now() 
    currentHour = int(now.strftime("%H"))
    if currentHour >= 8 and currentHour < 20:
        return True
    else:
        return False

@background
def StartQuestionaireReminder():
    print("Reminder Started at ", time.time())

    if not isReminderAllowedAtThisTime():
        return

    candidates = models.Person.objects.all()
    allCandidatesResponded = True
    for candidate in candidates:
        if candidate.status != 'Received':
             allCandidatesResponded = False
             candQuestionsUrl = "ec2-3-17-12-192.us-east-2.compute.amazonaws.com/questions?id={}".format(candidate.stringId)
             optout_link = 'ec2-3-17-12-192.us-east-2.compute.amazonaws.com/opt_out?id=' + candidate.stringId
             sendSMS("+919008718152", "xyz", candQuestionsUrl)
             send_email(candidate.name, "Developer","Moto Rockr","Dharwad","www.SlickHire.in","www.SlickHire.in/jobs", candQuestionsUrl, optout_link, "anthony_1087@yahoo.com")
             print("Reminder Sent")
             candidate.reminderscount += 1
             if candidate.reminderscount == 3:
                 candidate.delete()
'''
