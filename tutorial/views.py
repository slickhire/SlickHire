from django.shortcuts import render
from django.http import HttpResponse
from tutorial.functions import handle_uploaded_file  
from tutorial.forms import StudentForm  
from django.core.serializers import serialize
from django.http import JsonResponse
from . import models
from . import promStats
from django.views.decorators.csrf import csrf_exempt
import json
import random
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
import time
import json

import smtplib
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .twilioUtils import send_email
from .twilioUtils import sendSMS

def dashboard(request):
    if request.method == 'GET':
        jobIdList = list(models.JobProfile.objects.order_by().values_list('jobId', flat=True).distinct())
        return render(request, "dashboard.html", { 'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'jobIdList':jobIdList })

def jprofile(request):
   return render(request, "jprofile.html", { 'slickhire_host_url': settings.SLICKHIRE_HOST_URL })
@csrf_exempt
def deleteJob(request):
    try:
        data = models.JobProfile.objects.get(jobId__exact=request.POST['jobid'])
        if data:
        	data.delete()

    except models.JobProfile.DoesNotExist:
        print("")
    return HttpResponse("success")

def getJob(request):
    data = list(models.JobProfile.objects.values_list())
    return JsonResponse({"draw": 1, "recordsTotal": 1, "recordsFiltered": 1, "data": data}, safe=False)


def calendarCandidate(request):
    if request.method == 'GET':
        id = request.GET["id"]
        if id == "":
            return HttpResponse("Invalid Request")
        try:
            data = models.Person.objects.only('questions').get(stringId__exact=request.GET['id'])
            row = models.JobProfile.objects.get(jobId__exact=data.questions)

        except models.Person.DoesNotExist:
            return HttpResponse("Invalid Request")
        newVal = row.availSlots 

        if data.calendar != "":
            if row.availSlots == "[]":
                newVal = "[" + data.calendar + "]"
            else:
                # atleast one entry is there
                newVal = row.availSlots.replace("]", "," + data.calendar + "]")
        return render(request, "calendarCandidate.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'data': "[]" if newVal == "" else newVal, 'uid': request.GET['id']})

@csrf_exempt
def calendar(request):
    if request.method == 'GET':
        id = request.GET["id"]
        if id == "":
            return HttpResponse("Invalid Request")
        row = models.JobProfile.objects.get(jobId__exact=request.GET['id'])
        return render(request, "calendar.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'data': "[]" if row.calendar == "" else row.calendar, 'jobId': request.GET['id'], 'eventId': row.lastEventId})
    else:
        if request.POST['id'] != "":
            id = request.POST['id']
            row = models.JobProfile.objects.get(jobId__exact=id)
            print(row.calendar)
            if row.calendar == "":
                row.calendar = "[]"

            oldCalendar = json.loads(row.calendar)
            newCalendar = json.loads(request.POST['calendar'])

            newCalendarDictionary = {}
            availSlots = []
            for newEvent in newCalendar:
                newCalendarDictionary[newEvent["id"]] = 1
                print(newEvent, newEvent["backgroundColor"])
                if newEvent["backgroundColor"] == "#FFFFFF":
                    # this is new one
                    availSlots.append(newEvent)
                    print("list push", availSlots)

            for event in oldCalendar:
                if event["backgroundColor"] == "#FFA07A" and newCalendarDictionary.get(str(event["id"])) == None and "," + str(event["id"]) + "," not in request.POST['deletedEventsList']: 
                    return HttpResponse("One of the slot you have deleted is already booked, try again!!")

                if request.POST['deletedEventsList'] != "" and ("," + event["id"] + ",") in request.POST['deletedEventsList']:
                    user = models.Person.objects.get(stringId__exact=event["title"].split(",")[2])
                    print("candidate interview deleted", user.name)



            row.calendar = request.POST['calendar']
            row.availSlots = json.dumps(availSlots, indent=None, separators=(',', ':'))
            print("new avail slots", row.availSlots)
            row.lastEventId = request.POST['lastEventId']
            row.save()
        else:
            uid = request.POST['uid']
            user = models.Person.objects.get(stringId__exact=request.POST['uid'])
            id = user.questions
            row = models.JobProfile.objects.get(jobId__exact=id)
            print("post, calendar=", row.calendar, request.POST['calendar']) 
            
            if user.calendar != "":
                if "#FFA07A" not in request.POST['calendar']:
                    return HttpResponse("You already have booking")
                # cancel booking
                newVal = request.POST['calendar']
                newVal = newVal.replace("#FFA07A", "#FFFFFF");
                print("newVal", newVal)
                newVal = newVal.replace("\"title\":\"" + user.name + "," + user.mobile + "," + user.stringId + "\"", "\"title\":\"\"")
                print("cancelling and inserting", newVal)
                row.calendar = row.calendar.replace(request.POST['calendar'], newVal, 1)
                print("cancelled", row.availSlots)

                if row.availSlots != "[]":
                    print("cancell no avail slot")
                    newVal = "," + newVal
                row.availSlots = row.availSlots.replace("]", newVal + "]")

                user.calendar = ""
                user.save()
                row.save()
                return HttpResponse("Cancelled Successfully")

            if request.POST['calendar'] not in row.calendar:
                return HttpResponse("No Slots Available")

            newVal = request.POST['calendar']
            newVal = newVal.replace("#FFFFFF", "#FFA07A");
            print("newVal", newVal, user.name, "nameend")
            newVal = newVal.replace("\"title\":\"\"", "\"title\":\"" + user.name + "," + user.mobile + "," + user.stringId + "\"")
            print("booking nee val", newVal)
            row.calendar = row.calendar.replace(request.POST['calendar'], newVal, 1)
            print("before booking", row.availSlots)
            if row.availSlots != "[]":
                if "," + request.POST['calendar'] in row.availSlots:
                    row.availSlots = row.availSlots.replace("," + request.POST['calendar'], "", 1)
                elif request.POST['calendar'] + "," in row.availSlots:
                    #first element
                    row.availSlots = row.availSlots.replace(request.POST['calendar'] + ",", "", 1)
                else:
                    row.availSlots = row.availSlots.replace(request.POST['calendar'], "", 1)
            print("after booking", row.availSlots)
            user.calendar = newVal
            user.save()
            row.save()
        return HttpResponse("success")

@csrf_exempt
def sendInterviewLink(request):
    candidates = request.POST.getlist('candidates[]')
    for i in candidates:
        print(i)
        candidate = models.Person.objects.get(mobile__exact=i)
        candidate.status = "Invited"
        url = settings.SLICKHIRE_HOST_URL + "/calendarCandidate?id=" + candidate.stringId
        #res = send_mail("Book Interview Slot", url, settings.EMAIL_HOST_USER, candidate.email)
        send_mail('Book Interview Slot', url, settings.EMAIL_HOST_USER, [candidate.email], fail_silently = False)
        candidate.save()
    return HttpResponse("success")


@csrf_exempt
def sendLink(request):
    candidates = request.POST.getlist('candidates[]')
    candidatesStr = ' '.join(candidates);
    row = models.InternalLink(linkId=get_random_string(length=30), candidates=candidatesStr)
    print(row.linkId)
    row.save()
    data = models.Person.objects.only('questions').get(mobile__exact=candidates[0])
    emails = models.JobProfile.objects.only('emails').get(jobId__exact=data.questions)
    url = settings.SLICKHIRE_HOST_URL + "/getLink?linkId=" + row.linkId
    res = send_mail("Candidate Shortlisted", url, settings.EMAIL_HOST_USER, emails.emails.split(","))
    print(candidatesStr)
    return HttpResponse("success")

def getLinkData(request):
    linkId = request.GET["linkId"]
    print(linkId)
    data = models.InternalLink.objects.get(linkId__exact=linkId)
    print("candidates saved are", data.candidates)
    splits = data.candidates.split()
    print(splits)

    candList = []
    #for loop to iterate over words array
    for cid in splits:
        print(cid)
        candidate = models.Person.objects.values_list('checkbox', 'name', 'mobile', 'experience','institute', 'education', 'employer', 'skills', 'score', 'email', 'status').get(mobile__exact=cid)
        candList.append(list(candidate))
        print(candidate, candList)
 
    return JsonResponse({"draw": 1, "recordsTotal": 1, "recordsFiltered": 1, "data": candList}, safe=False)

def getLink(request):
    linkId = request.GET["linkId"]
    if linkId == "":
        return HttpResponse("Invalid Request")
    try:
        data = models.InternalLink.objects.get(linkId__exact=linkId)
    except models.InternalLink.DoesNotExist:
        return HttpResponse("Invalid Request")


    return render(request,"getLink.html",{'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'linkId':linkId})

@csrf_exempt
def saveJob(request):
	print("save")
	salary = []
	if '-' in request.POST['salary']:
		salary = request.POST['salary'].split('-')
	else:
		salary.append(request.POST['salary'])
		salary.append(request.POST['salary'])

	exp = []
	if '-' in request.POST['exp']:
		exp = request.POST['exp'].split('-')
	else:
		exp.append(request.POST['exp'])
		exp.append(request.POST['exp'])

	notice = []
	if '-' in request.POST['notice']:
		notice = request.POST['notice'].split('-')
	else:
		notice.append(request.POST['notice'])
		notice.append(request.POST['notice'])

	job = models.JobProfile(jobId=request.POST['jobid'], designation=request.POST['designation'], experience = request.POST['exp'], salary = request.POST['salary'], notice = request.POST['notice'], skills = request.POST['skills'], salary1 = salary[0], salary2 = salary[1], exp1 = exp[0], exp2 = exp[1], notice1 = notice[0], notice2 = notice[1], emails=request.POST['emails'], onlineProgExamCategory=request.POST['onlineProgExamCategory'], onlinePrefProgLang=request.POST['prefProgLang'], onlinePassPercentage=request.POST['passPercentage'])
	if request.POST['onlineProgExamCategory'] != "none":
		onlineques = models.OnlineTestKeys.objects.filter(category=request.POST['onlineProgExamCategory'])
		random_index = []
		questions = []
		random_index = random.sample(range(1, models.OnlineTestKeys.objects.filter(category=request.POST['onlineProgExamCategory']).count()+1), 5)
		looper = 1
		print("Ganga", models.OnlineTestKeys.objects.filter(category=request.POST['onlineProgExamCategory']).count(),len(onlineques))
		print("here",random_index,onlineques)
		for option in onlineques:
			try:
				dummy = random_index.index(looper)
				print("looper",looper,dummy)
				questions.append(option)
			except ValueError:
				looper = looper + 1
				continue
			if (looper == models.OnlineTestKeys.objects.filter(category=request.POST['onlineProgExamCategory']).count()):
				break
			looper = looper + 1
		print("Ganga qurestion length",len(questions),len(random_index),looper)
		print(request.POST['onlineProgExamCategory'])
		job.question1 = questions[0].qid 
		job.question2 = questions[1].qid
		job.question3 = questions[2].qid
		job.question4 = questions[3].qid
		job.question5 = questions[4].qid
		print("Ganga Qid",questions[0].qid,questions[1].qid,questions[2].qid,questions[3].qid,questions[4].qid)
	job.save()
	return HttpResponse("success")

@csrf_exempt
def upload(request):
    if request.method == 'POST':
        student = StudentForm(request.POST, request.FILES)
        print("Post received", student.is_valid(), request.FILES['file'], request.POST['jobId'])
        if student.is_valid():
            handle_uploaded_file(request.FILES['file'], request.POST['jobId'])
            return HttpResponse("File uploaded successfuly")
    else:
        jobIdList = list(models.JobProfile.objects.order_by().values_list('jobId', flat=True).distinct())
        student = StudentForm()
        return render(request,"upload.html",{'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'form':student, 'jobIdList':jobIdList})

def getJobIdList(request):
    jobIdList = list(models.JobProfile.objects.order_by().values_list('jobId', flat=True).distinct())
    responsestr = ','.join([str(elem) for elem in jobIdList]) 
    return HttpResponse(responsestr)

def index(request):  
    if request.method == 'POST': 
        student = StudentForm(request.POST, request.FILES)
        if student.is_valid():
            handle_uploaded_file(request.FILES['file'])  
            return HttpResponse("File uploaded successfuly")  
    else: 
        jobIdList = list(models.JobProfile.objects.order_by().values_list('jobId', flat=True).distinct())
        student = StudentForm()
        return render(request,"index.html",{'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'form':student, 'jobIdList':jobIdList})    

def data(request):
    data = list(models.Person.objects.values_list().filter(questions=request.GET['jobId']))
    return JsonResponse({"draw": 1, "recordsTotal": 1, "recordsFiltered": 1, "data": data}, safe=False)
  
def GetScore(percentage, threshold1, threshold2, value):
    if int(threshold1) > int(value):
        diff = int(threshold1) - int(value)
    elif int(threshold2) < int(value):
        diff = int(value) - int(threshold2)
    if diff > 10:
        return 0
    return ((10 - diff)  * (percentage / 10))

def questions(request):
    if request.method == 'POST':
        data = models.Person.objects.only('questions').get(stringId__exact=request.POST['strId'])
        data.status = "Interested"
        data.nextReminderTimestamp = 0
        row = models.JobProfile.objects.get(jobId__exact=data.questions)
        score = 0
        data.experience = request.POST['experience']
        data.salary = request.POST['currentCtc']
        data.employer = request.POST['company']
        data.expectedCtc = request.POST['expectedCtc']
        data.notice = request.POST['notice']
        skills = row.skills.split(',')
        weightPerQuestion = 100 / (3 + len(skills))
        if int(row.exp1) <= int(data.experience) <= int(row.exp2):
            score += weightPerQuestion 
        else:
            score += GetScore(int(weightPerQuestion), row.exp1, row.exp2, data.experience)
        
        if int(row.salary1) <= int(data.expectedCtc) <= int(row.salary2):
            score += weightPerQuestion
        elif int(row.salary1) > int(data.expectedCtc) :
            score += weightPerQuestion
        else:
            score += GetScore(int(weightPerQuestion), row.salary1, row.salary2, data.expectedCtc)
   
        if int(row.notice1) <= int(data.notice) <= int(row.notice2):
            score += weightPerQuestion
        elif int(row.notice1) > int(data.notice):
            score += weightPerQuestion
        else:
            score += GetScore(int(weightPerQuestion), row.notice1, row.notice2, data.notice)

        for q in skills:
            score += (int(request.POST[q]) * weightPerQuestion) / 10
        data.score = score
        print("Ganga",request.POST.get('progLang'))
        if request.POST.get('progLang') is None:
            progLang = row.onlinePrefProgLang
            data.onlinePrefProgLang = row.onlinePrefProgLang 
        else:
            progLang = request.POST.get('progLang')
            data.onlinePrefProgLang = request.POST.get('progLang')

        if progLang == "python":
            data.onlineProgLangCM = "python"
            data.onlineProgLangIDE = "Python"
        elif progLang == "cpp":
            data.onlineProgLangCM = "clike"
            data.onlineProgLangIDE = "Cpp"
        elif progLang == "java":
            data.onlineProgLangCM = "text/x-java"
            data.onlineProgLangIDE = "Java"
        else:
            print("Do Nothing")

        if row.onlineProgExamCategory != "none":
            onlinelink = settings.SLICKHIRE_HOST_URL + "/online?id=" + request.POST['strId']
            optoutlink = settings.SLICKHIRE_HOST_URL + '/opt_out?id=' + request.POST['strId']
            jobConfig = models.JobSettings.objects.get(companyId="1")
            if jobConfig:
                if jobConfig.smsEnabled:
                    smsStatus = ''
                    sendSMS(data.mobile, "xyz", onlinelink)
                    print(smsStatus)
                if jobConfig.emailEnabled:
                    send_email(data.name, \
                               row.designation, \
                               "Moto Rockr", \
                               "Dharwad", \
                               "www.SlickHire.in", \
                               "www.SlickHire.in/jobs", \
                               onlinelink, \
                               optoutlink, \
                               data.email,\
                               online=True)
                    print("Online Mail Sent",onlinelink)
             
        row.save()

        promStats.candidates_count.labels("1", data.questions, "Interested").inc()
        promStats.candidates_state_transition.labels("1", data.questions, "Subscribed").observe(
					((int(time.time()) - data.statusTimestamp) / 3600))
        data.statusTimestamp = int(time.time())
        
        data.save()
        
        return HttpResponse("Data submitted successfuly" + request.POST['strId'])
    else:
        id = request.GET["id"]
        if id == "":
            return HttpResponse("Invalid Request")
        try:
            print(id)
            data = models.Person.objects.only('questions').get(stringId__exact=id)
        except models.Person.DoesNotExist:
            return HttpResponse("Candidate Not Found")

        row = models.JobProfile.objects.get(jobId__exact=data.questions)
        skillList = []
        for x in row.skills.split(','):
            skillList.append(x)

        data.question1 = row.question1
        data.question2 = row.question2
        data.question3 = row.question3
        data.question4 = row.question4
        data.question5 = row.question5
        data.nextReminderTimestamp = int(time.time()) + 86400
        data.save()
        selectLang = "false"
        if row.onlineProgExamCategory != "none" and row.onlinePrefProgLang == "any":
            selectLang = "true" 

        return render(request,"questions.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'qs': skillList, 'stringId': id, 'selectLang': selectLang})

def opt_out(request):
    if request.method == 'POST': 
        print('Receieved POST opt-out request for: ', request.POST["strId"])
        candidate = models.Person.objects.only('questions').get(stringId__exact=request.POST['strId'])
        if candidate:
            promStats.candidates_count.labels("1", candidate.questions, "OptedOut").inc()
            subscribedStatusTime = (int(time.time()) - candidate.statusTimestamp) / 3600
            print("Timestamp: ", subscribedStatusTime)
            promStats.candidates_state_transition.labels("1", candidate.questions, "Subscribed").observe(subscribedStatusTime)
            candidate.delete()
            return HttpResponse("You have successfuly opted-out")
        else:
            return HttpResponse("Invalid Request")
    else:
        print('Receieved GET opt-out request for: ', request.GET["id"])
        return render(request,"optout.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'stringId': request.GET["id"]})


def homepage(request):
    return HttpResponse("First App")

def clientSettings(request):
    config = models.JobSettings.objects.get(companyId__exact="1")
    if settings:
        return render(request, "settings.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, "jobSettings": config })
    else:
        return render(request, "settings.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, "jobSettings": models.JobSettings() })

def jobSettings(request):
	config = models.JobSettings( \
				companyId="1",
               	smsEnabled=request.POST.get('sms', False),
				whatsappEnabled=request.POST.get('Whatsapp', False),
				emailEnabled=request.POST.get('email', False),
				voiceEnabled=request.POST.get('voice', False),
				remindersCount=request.POST.get('remindCount', 0))
	config.save()
	return HttpResponse("Settings Saved")

def online(request):
    if request.method == 'POST':
        data = models.Person.objects.only('questions').get(stringId__exact=request.POST['strId'])
        print(request.POST.get("answer1"))
        if request.POST.get("answer1") is not None:
            data.answer1 = request.POST.get("answer1")
            data.onlineAnswer1Time += int(time.time()) - data.onlineStartTimeStamp 
            data.onlineStartTimeStamp = int(time.time())
            data.save()
            q2 = models.OnlineTestKeys.objects.get(qid=data.question2)
            res = zip([['2',q2.type,q2.question,q2.choice1,q2.choice2,q2.choice3,q2.choice4,data.answer2]])
            return render(request,"onlinetest.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'qs': res, 'stringId': request.POST['strId'], 'onlineProgLangCM' :data.onlineProgLangCM, 'onlineProgLangIDE':data.onlineProgLangIDE})
        elif request.POST.get("answer2") is not None:
            data.answer2 = request.POST.get("answer2")
            data.onlineAnswer2Time += int(time.time()) - data.onlineStartTimeStamp
            data.onlineStartTimeStamp = int(time.time())
            data.save()
            q3 = models.OnlineTestKeys.objects.get(qid=data.question3)
            print("Ganga",data.answer3, q3.question)
            print("Ganga",data.onlineProgLangCM,data.onlineProgLangIDE)
            res = zip([['3',q3.type,q3.question,q3.choice1,q3.choice2,q3.choice3,q3.choice4,data.answer3]])
            return render(request,"onlinetest.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'qs': res, 'stringId': request.POST['strId'], 'onlineProgLangCM' :data.onlineProgLangCM, 'onlineProgLangIDE':data.onlineProgLangIDE})
        elif request.POST.get("answer3") is not None:
            data.answer3 = request.POST.get('answer3')
            data.onlineAnswer3Time += int(time.time()) - data.onlineStartTimeStamp
            data.onlineStartTimeStamp = int(time.time())
            data.save()
            print("Ganga", data.answer3)
            q4 = models.OnlineTestKeys.objects.get(qid=data.question4)
            res = zip([['4',q4.type,q4.question,q4.choice1,q4.choice2,q4.choice3,q4.choice4,data.answer4]])
            return render(request,"onlinetest.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'qs': res, 'stringId': request.POST['strId'], 'onlineProgLangCM' :data.onlineProgLangCM, 'onlineProgLangIDE':data.onlineProgLangIDE})
        elif request.POST.get("answer4") is not None:
            data.answer4 = request.POST.get('answer4')
            data.onlineAnswer4Time += int(time.time()) - data.onlineStartTimeStamp
            data.onlineStartTimeStamp = int(time.time())
            data.save()
            q5 = models.OnlineTestKeys.objects.get(qid=data.question5)
            res = zip([['5',q5.type,q5.question,q5.choice1,q5.choice2,q5.choice3,q5.choice4,data.answer5]])
            return render(request,"onlinetest.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'qs': res, 'stringId': request.POST['strId'], 'onlineProgLangCM' :data.onlineProgLangCM, 'onlineProgLangIDE':data.onlineProgLangIDE})
        elif request.POST.get("answer5") is not None:
            data.status = "Received"
            data.answer5 = request.POST.get('answer5')
            data.onlinetestcomplete = 1
            data.onlinetesteval = 0
            data.onlineAnswer5Time += int(time.time()) - data.onlineStartTimeStamp
            data.onlineStartTimeStamp = int(time.time())
            data.save()
            return HttpResponse("Answers submitted successfuly" + data.answer1 + data.answer2 + data.answer3 + data.answer4 + data.answer5)
        else:
            data.onlinetestcomplete == 1
            return HttpResponse("Timed out")
    else:
        id = request.GET["id"]
        if id == "":
            return HttpResponse("Invalid Request")
        try:
            print(id)
            data = models.Person.objects.only('questions').get(stringId__exact=id)  
            if data.onlinetestcomplete == 1:
                return HttpResponse("<h3>Online test submitted already.<h3>")            
            q1 = models.OnlineTestKeys.objects.get(qid=data.question1)
            res = zip([['1', q1.type,q1.question,q1.choice1,q1.choice2,q1.choice3,q1.choice4,data.answer1]])
            data.onlineStartTimeStamp = int(time.time())
            data.save()
            return render(request,"onlinetest.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'qs': res, 'stringId': id, 'onlineProgLangCM' :data.onlineProgLangCM, 'onlineProgLangIDE':data.onlineProgLangIDE})
        except models.Person.DoesNotExist:
            return HttpResponse("Profile not exists to take online test")

def add_questions(request):
    if request.method == 'POST':
        for key, values in request.POST.lists():
            print(key, values)
        if request.POST.get("type") == "program":
            return render(request,"setOnline.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'type': "program"})  
        if request.POST.get("type") == "multiple-choice":   
            return render(request,"setOnline.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'type': "multiple-choice"})
        if request.POST.get("question-choice") is not None:            
            if request.POST.getlist("choices") is None:
               return HttpResponse("Choices MUST be submitted")
            if len(request.POST.getlist("choices")) != 4:
               return HttpResponse("Maximum 4 choices MUST be submitted")
            if request.POST.get("answer") is None:
               return HttpResponse("Answer is mandatory for evaluation")
            if request.POST.get("answer") not in set(request.POST.getlist("choices")) :
               return HttpResponse("Answer MUST be one of the option provided")
            if request.POST.get("category") is None:
               return HttpResponse("Category is mandatory")
            choice1 = request.POST.getlist("choices")[0]
            choice2 = request.POST.getlist("choices")[1]
            choice3 = request.POST.getlist("choices")[2]
            choice4 = request.POST.getlist("choices")[3]
            latest = models.OnlineTestKeys.objects.latest('qid')
            r = models.OnlineTestKeys(qid=latest.qid+1, type=1, question=request.POST.get("question-choice"), choice1=choice1, choice2=choice2, choice3=choice3, choice4=choice4, answer=request.POST.get("answer"), category = request.POST.get("category"))
            r.save()
        if request.POST.get("question") is not None:
            if request.POST.getlist("input") is None:
                return HttpResponse("Testcases(input) are mandatory")
            if request.POST.getlist("output") is None:
                return HttpResponse("Testcases(output) are mandatory")
            inputs = request.POST.getlist("input")
            outputs = request.POST.getlist("output")            
            if request.POST.get("category") is None:
               return HttpResponse("Category is mandatory")
            test1 = inputs[0] + ';' + outputs[0]
            test2 = 'null'
            test3 = 'null'
            test4 = 'null'
            test5 = 'null'
            try:
                test2 = inputs[1] + ';' + outputs[1]
                test3 = inputs[2] + ';' + outputs[2]
                test4 = inputs[3] + ';' + outputs[3]
                test5 = inputs[4] + ';' + outputs[4]
            except IndexError:
                print("Handle the exception")                
               
            latest = models.OnlineTestKeys.objects.latest('qid')            
            r = models.OnlineTestKeys(qid=latest.qid+1, type=0, question=request.POST.get("question"), category = request.POST.get("category"), test1=test1, test2=test2, test3=test3, test4=test4, test5=test5)
            r.save()                   
        return HttpResponse("Data submitted successfuly" + request.POST['strId'])
    else:        
        return render(request,"setOnline.html", {'slickhire_host_url': settings.SLICKHIRE_HOST_URL, 'type': "none"})

def updateActivity(request):
	print("Ganga",request.POST.get("id"), request.POST.get("totalTime"))
	if request.method == 'POST':
		data = models.Person.objects.only('questions').get(stringId__exact=request.POST['id'])		    
		if int(request.POST.get("totalTime")) > data.onlineTestTimePending:
			print("Here you go, i caught you buddy")
			return HttpResponse(data.onlineTestTimePending)
		else:
			data.onlineTestTimePending = request.POST.get("totalTime")
			data.save()
			return HttpResponse(data.onlineTestTimePending)

def printquestions(request):
        data = list(models.OnlineTestKeys.objects.values_list())    
        return JsonResponse({"draw": 1, "recordsTotal": 1, "recordsFiltered": 1, "data": data}, safe=False)

def printPersons(request):
    data = list(models.Person.objects.values_list())
    return  JsonResponse({"draw": 1, "recordsTotal": 1, "recordsFiltered": 1, "data": data}, safe=False)

def printjobs(request):
    data = list(models.JobProfile.objects.values_list())
    return  JsonResponse({"draw": 1, "recordsTotal": 1, "recordsFiltered": 1, "data": data}, safe=False)
# Create your views here.

@csrf_exempt
def pegStats(request):
	print("Pegging Stats")
	promStats.candidates_count.labels( \
									  request.POST['company_name'], \
									  request.POST['job_profile'], \
									  request.POST['candidate_state']).inc(int(request.POST['stat_value']))
	candPreviousState = request.POST['candidate_previous_state']
	if candPreviousState != "":
		promStats.candidates_state_transition.labels( \
									  request.POST['company_name'], \
									  request.POST['job_profile'], \
									  request.POST['candidate_previous_state']) \
									  .observe(((int(time.time()) - int(request.POST['candidate_previous_state_time'])) / 3600))
	return HttpResponse("Success")
