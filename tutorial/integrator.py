# Notifier example from tutorial
#
# See: http://github.com/seb-m/pyinotify/wiki/Tutorial
#
from zipfile import ZipFile
import os, shutil, time, sys
from datetime import datetime
#sys.path.insert(1, '/home/ubuntu/ResumeParser/resume_parser/resume_parser')
from . import resume_parser
from django.utils.crypto import get_random_string
from . import models
from background_task import background
from django.contrib.auth.models import User
from twilio.rest import Client
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail,EmailMessage
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.template import Context

ACCOUNT_SID = "ACbe9ca3f562c7d7fe80fc560db69fa588"
AUTH_TOKEN = "9a8ffae380118f71a6e693956c34a4b5"
SMS_NUMBER = "+18125788368"
MESSAGING_SERVICE_ID = "MG5eb6a2e338a34fa801960c2a827522d3"
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
	id = "ec2-3-17-12-192.us-east-2.compute.amazonaws.com/questions?id=" + p.stringId
	optout_link = 'ec2-3-17-12-192.us-east-2.compute.amazonaws.com/opt_out?id=' + p.stringId
	jobConfig = models.JobSettings.objects.get(companyId="1")
	if jobConfig:
		if jobConfig.smsEnabled:
			sendSMS(p.mobile, "xyz", id)
		if jobConfig.voiceEnabled:
			makeVoiceCall(p.mobile, "kempa")
		if jobConfig.emailEnabled:
			send_email(rparser['name'],"Devloper","Moto Rockr","Dharwad","www.SlickHire.in","www.SlickHire.in/jobs",id, optout_link, p.email)
	p.save()
	jobStats = models.JobProfile.objects.get(jobId__exact=p.questions)
	jobStats.candidatesCount += 1
	jobStats.save()

def Extract_Files(newFile):
	print('Extract single file from ZIP', newFile)
	with ZipFile(newFile, 'r') as zipObj:
		listOfFileNames = zipObj.namelist()
		for fileName in listOfFileNames:
			zipObj.extract(fileName)
			print('Processing the new file',fileName)
			parser = resume_parser.ResumeParser(fileName)
			AddPerson(parser.get_extracted_data())

@background(schedule=5)
def CallHandler():
    print("Checking for any uploaded files")
    uploadedFiles = os.listdir(os.path.join(settings.BASE_DIR, 'tutorial/static/upload/'))
    for uploadedFile in uploadedFiles:
        print(uploadedFile)
        filename = os.path.join(settings.BASE_DIR, 'tutorial/static/upload/', uploadedFile)
        if os.path.splitext(uploadedFile)[-1].lower() == ".zip":
            Extract_Files(filename)
        shutil.move(filename, os.path.join(settings.BASE_DIR, 'tutorial/static/processed/'))
            
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
    
    jobConfig = models.JobSettings.objects.get(companyId="1")
    if not jobConfig:
        return

    if jobConfig.remindersCount == 0:
        return

    currentTimestamp = int(time.time())

    candidates = models.Person.objects.all()
    for candidate in candidates:
        if candidate.status != 'Received' and currentTimestamp >= candidate.nextReminderTimestamp:
            candQuestionsUrl = "ec2-3-17-12-192.us-east-2.compute.amazonaws.com/questions?id={}".format(candidate.stringId)
            optout_link = 'ec2-3-17-12-192.us-east-2.compute.amazonaws.com/opt_out?id=' + candidate.stringId
            if jobConfig.smsEnabled:
            	sendSMS(candidate.mobile, "xyz", id)
            if jobConfig.voiceEnabled:
            	makeVoiceCall(candidate.mobile, "kempa")
            if jobConfig.emailEnabled:
            	send_email(rparser['name'],"Devloper","Moto Rockr","Dharwad","www.SlickHire.in","www.SlickHire.in/jobs",id, optout_link, candidate.email)
            print("Reminder Sent")
            candidate.reminderscount += 1
            if candidate.reminderscount == jobConfig.remindersCount:
                candidate.delete()
                jobStats = models.JobProfile.objects.get(jobId__exact=candidate.questions)
                jobStats.discardedCount += 1
                jobStats.save()
            else:
                candidate.nextReminderTimestamp = currentTimestamp + 86400
                candidate.save()
