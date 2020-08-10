# Notifier example from tutorial
#
# See: http://github.com/seb-m/pyinotify/wiki/Tutorial
#
import os, shutil, time, sys
import requests, json

from zipfile import ZipFile
from datetime import datetime

from . import resume_parser
from . import models
from . import promStats

from .twilioUtils import sendSMS
from .twilioUtils import makeVoiceCall
from .twilioUtils import send_email

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
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from pwd import getpwnam  
import grp
import spacy
import getpass
import en_core_web_sm
import os
import multiprocessing
import subprocess

def updateCandidateStatus(mobileNo, jobId, state, reason=""):
    candidateEntry = models.CandidateHistory.objects.get(mobile=mobileNo)
    print("Hello", candidateEntry.status)
    candidateStatus = json.loads(candidateEntry.status)
    jobIdExists = False
    for jobEntry in candidateStatus:
        if jobId in jobEntry:
            jobIdExists = True
            jobEntry["state"] = state
            jobEntry["stateTimestamp"] = int(time.time())
            jobEntry["reason"] = reason
    if not jobIdExists:
        newJobEntry = {}
        newJobEntry["jobId"] = jobId
        newJobEntry["state"] = state
        newJobEntry["stateTimestamp"] = int(time.time())
        newJobEntry["reason"] = reason
        candidateStatus.append(newJobEntry)
    candidateEntry.status = json.dumps(candidateStatus)
    print(candidateEntry.status)
    candidateEntry.save()

def AddPerson(rparser, jobId):
        print("latest",rparser['name'],rparser['email'],rparser['mobile_number'], rparser['skills'], jobId)
        if models.CandidateHistory.objects.filter(mobile=rparser['mobile_number']).exists():
            candidateEntry = models.CandidateHistory.objects.get(mobile=rparser['mobile_number'])
            print("Lovely", rparser['mobile_number'], " ", candidateEntry.status)
            candidateStatus = json.loads(candidateEntry.status)
            if jobId in candidateStatus and (candidateStatus[jobId]['stateTimestamp'] - int(time.time()) < (6*30*24*60*60)):
                #return None TODO
                print("Candidate already exists")
        else:
            candidateEntry = models.CandidateHistory(name=rparser['name'],  \
                                                    mobile=rparser['mobile_number'], \
                                                    email=rparser['email'])
            candidateEntry.save()
        print("Ganga Rama here")
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
        questions_link = settings.SLICKHIRE_HOST_URL + "/questions?id=" + p.stringId
        print(questions_link)
        optout_link = settings.SLICKHIRE_HOST_URL + '/opt_out?id=' + p.stringId
        jobConfig = models.JobSettings.objects.get(companyId="1")
        # TODO: Fix it once company object is created
        if True or jobConfig:
        	if True or jobConfig.smsEnabled:
        		smsStatus = ''
        		sendSMS(p.mobile, "xyz", questions_link)
        		print(smsStatus)
        	if True or jobConfig.voiceEnabled:
        		makeVoiceCall(p.mobile, "kempa")
        	if True or jobConfig.emailEnabled:
        		send_email(rparser['name'], \
        				   jobProfile.designation, \
                       "Moto Rockr", \
                       "Dharwad", \
                       "www.SlickHire.in", \
                       "www.slickhire.in/jobs", \
                       questions_link, \
                       optout_link, \
                       p.email,\
                       online=False)
        p.status = "Subscribed"
        p.statusTimestamp = int(time.time())
        p.save()
        updateCandidateStatus(rparser['mobile_number'], jobId, "Subscribed")

def makeDict(parser):
    details = {}
    for x in parser.split('\n'):
        if x is not "":
            data = x.split(':')
            if data is not "":
                details[data[0].replace(" ", "")] = data[1].replace(" ", "")
    return(details)


def Extract_Files(newFile):
    print('Extract single file from ZIP', newFile)
    jobId = newFile.split('/', -1)[-1].split('#', 1)[0]
    numSubscribers = 0
    os.chdir(os.path.join(settings.BASE_DIR, 'tmp/'))
    with ZipFile(newFile, 'r') as zipObj:
        listOfFileNames = zipObj.namelist()
        for fileName in listOfFileNames:
            print(fileName)
            zipObj.extract(fileName)
            #Enable the resume_parser.ResumeParser once nlp.load is fixed
            print('Processing the new file',fileName)
            command = "python3 /root/backend/SlickHire/tutorial/rp.py " + fileName
            parser = subprocess.check_output(command, shell=True,universal_newlines=True)
            AddPerson(makeDict(parser), jobId)
            #parser = resume_parser.ResumeParser(fileName)
            #AddPerson(parser.get_extracted_data(), jobId)
            numSubscribers += 1
    requests.post(settings.SLICKHIRE_HOST_URL + "/pegStats", \
        data=\
        {
            'csrfmiddlewaretoken': 'HelloWorld', \
            'company_name': '1', \
            'job_profile': jobId, \
            'candidate_state': 'Subscribed', \
            'stat_value': numSubscribers, \
            'candidate_previous_state': '' \
        }, verify=False)


def OnlineTestEval():
    while 1:
        try:
            if  models.Person.objects.filter(onlinetesteval=0).exists():
                onlineeval = models.Person.objects.filter(onlinetesteval=0)
                score = 0
                for eval in onlineeval:
                    print("processing", eval.name)
                    try:
                        q1 = models.OnlineTestKeys.objects.get(qid=eval.question1)
                        q2 = models.OnlineTestKeys.objects.get(qid=eval.question2)
                        q3 = models.OnlineTestKeys.objects.get(qid=eval.question3)
                        q4 = models.OnlineTestKeys.objects.get(qid=eval.question4)
                        q5 = models.OnlineTestKeys.objects.get(qid=eval.question5)
                    except Content.DoesNotExist:
                        break	 
                    data = ([[q1, eval.answer1],[q2, eval.answer2],[q3, eval.answer3],[q4, eval.answer4],[q5, eval.answer5]])
                    try:
                        for ques, ans in data:
                            if ques.type:
                                if ques.answer == ans:
                                    score += 10
                            else:
                                tests = [ques.test1, ques.test2, ques.test3, ques.test4, ques.test5]
                                for test in tests:
                                    if test != "null":
                                        url = 'https://ide.geeksforgeeks.org/main.php'
                                        data = {'lang': eval.onlineProgLangIDE, 'code': ans, 'input': test.split(';', 1)[0], 'save': 'false'}
                                        headers= {'origin':'https://ide.geeksforgeeks.org/'}
                                        response = requests.post(url, data , headers=headers)
                                        print(response.status_code)
                                        print(response.text)
                                        jsonRes = response.json()
                                        print(jsonRes['sid'])
                                        sid = jsonRes['sid']
                                        # After 10 retries , we will declare that IDE has some issues and retry later.
                                        retry = 0
                                        while True:
                                            data = {'requestType': "fetchResults", 'sid' : sid } 
                                            response = requests.post('https://ide.geeksforgeeks.org/submissionResult.php', data , headers=headers)
                                            print(response.status_code)
                                            print(response.text)
                                            outputres = response.json()
                                            retry += 1
                                            if  outputres['status'] == 'SUCCESS' or retry == 100:        
                                                break
                                        # Have an error counter to know that ide is misbehaving
                                        if retry == 100:
                                            break
                                        if outputres['compResult'] == 'S' and test.split(';', 1)[1] == outputres['output']:
                                            score += 10
                                        # Additonally have a stat per Person to know how many programs resuled in compilation errors
                                        if outputres['compResult'] != 'S':
                                            eval.onlinetestcompileerrors += 1                        
                                        print(test.split(';', 1)[0])
                                        print(test.split(';', 1)[1])
                                        print(outputres['output'])
                        if retry == 100:
                            break
                        eval.onlinetestscore = score
                        eval.onlinetesteval = 1
                        eval.save()
                        break
                    except KeyError:
                        # Error counter to know that response from IDE is not proper.
                        eval.onlinetestscore = 0
                        eval.onlinetesteval = 0
                        eval.save()
            time.sleep(8)
        except ObjectDoesNotExist:
            time.sleep(8)

def ResumeHandler():
	while 1:
		uploadedFiles = os.listdir(os.path.join(settings.BASE_DIR, 'tutorial/static/upload/'))
		for uploadedFile in uploadedFiles:
			print(uploadedFile)
			filename = os.path.join(settings.BASE_DIR, 'tutorial/static/upload/', uploadedFile)
			if os.path.splitext(uploadedFile)[-1].lower() == ".zip":
				#os.chown(filename, getpwnam('www-data').pw_uid, grp.getgrnam('www-data')[2])
				Extract_Files(filename)
			shutil.move(filename, os.path.join(settings.BASE_DIR, 'tutorial/static/processed/'))
		time.sleep(5)
            
def isReminderAllowedAtThisTime():
    now = datetime.now() 
    currentHour = int(now.strftime("%H"))
    if currentHour >= 8 and currentHour < 20:
        return True
    else:
        return False


def StartQuestionaireReminder():
    while 1:
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
            if candidate.status != 'Interested' and currentTimestamp >= candidate.nextReminderTimestamp:
                candQuestionsUrl = settings.SLICKHIRE_HOST_URL + "/questions?id={}".format(candidate.stringId)
                optout_link = settings.SLICKHIRE_HOST_URL + '/opt_out?id=' + candidate.stringId
                if jobConfig.smsEnabled:
                    sendSMS(candidate.mobile, "xyz", id)
                if jobConfig.voiceEnabled:
                    makeVoiceCall(candidate.mobile, "kempa")
                if jobConfig.emailEnabled:
                    send_email(candidate.name,"Devloper","Moto Rockr","Dharwad","www.SlickHire.in","www.SlickHire.in/jobs",id, optout_link, candidate.email, False)
                candidate.reminderscount += 1
                if candidate.reminderscount == jobConfig.remindersCount:
                    requests.post(settings.SLICKHIRE_HOST_URL + "/pegStats", \
                        data=\
                        {
                                'company_name': '1', \
                                'job_profile': candidate.questions, \
                                'candidate_state': 'Discarded', \
                                'stat_value': 1, \
                                'candidate_previous_state': 'Subscribed', \
                                'candidate_previous_state_time': currentTimestamp \
                        }, verify=False)
                updateCandidateStatus(candidate.mobile, candidate.questions, "Discarded")
                candidate.delete()
            else:
                candidate.nextReminderTimestamp = currentTimestamp + 86400
                candidate.save()
        time.sleep(10)
