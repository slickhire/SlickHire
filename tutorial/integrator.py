# Notifier example from tutorial
#
# See: http://github.com/seb-m/pyinotify/wiki/Tutorial
#
import os, shutil, time, sys

from zipfile import ZipFile
from datetime import datetime

from . import resume_parser
from . import models

from background_task import background
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail,EmailMessage
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.template import Context

from . import twilioUtils

def AddPerson(rparser, jobId):
	print("latest",rparser['name'],rparser['email'],rparser['mobile_number'], rparser['skills'])
	jobProfile = models.JobProfile.objects.get(jobId__exact=jobId)
	p = models.Person(name=rparser['name'],  \
                      mobile=rparser['mobile_number'], \
                      stringId = get_random_string(length=30), \
					  questions = jobProfile.jobId,email=rparser['email'], \
					  skills=set(jobProfile.skills).intersection(set(rparser['skills'])), \
					  status="pending", \
                      score=0, \
                      education=rparser['education'], \
                      experience=rparser['experience'], \
                      reminderscount=0)
	questions_link = "ec2-3-17-12-192.us-east-2.compute.amazonaws.com/questions?id=" + p.stringId
	optout_link = 'ec2-3-17-12-192.us-east-2.compute.amazonaws.com/opt_out?id=' + p.stringId
	jobConfig = models.JobSettings.objects.get(companyId="1")
	if jobConfig:
		if jobConfig.smsEnabled:
			smsStatus = ''
			sendSMS(p.mobile, smsStatus, questions_link)
			print(smsStatus)
		if jobConfig.voiceEnabled:
			makeVoiceCall(p.mobile, "kempa")
		if jobConfig.emailEnabled:
			send_email(rparser['name'], \
					   jobProfile.desgination, \
                       "Moto Rockr", \
                       "Dharwad", \
                       "www.SlickHire.in", \
                       "www.SlickHire.in/jobs", \
                       questions_link, \
                       optout_link, \
                       p.email)
	p.save()
	jobProfile.candidatesCount += 1
	jobProfile.save()

def Extract_Files(newFile):
	print('Extract single file from ZIP', newFile)
	jobId = newFile.split('.', -1)[0].split('_', -1)[1]
	with ZipFile(newFile, 'r') as zipObj:
		listOfFileNames = zipObj.namelist()
		for fileName in listOfFileNames:
			zipObj.extract(fileName)
			print('Processing the new file',fileName)
			parser = resume_parser.ResumeParser(fileName)
			AddPerson(parser.get_extracted_data(), jobId)

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
