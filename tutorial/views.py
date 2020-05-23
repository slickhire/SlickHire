from django.shortcuts import render
from django.http import HttpResponse
from tutorial.functions import handle_uploaded_file  
from tutorial.forms import StudentForm  
from django.core.serializers import serialize
from django.http import JsonResponse
from . import models
from .tasks import online_test_eval
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from time import time

def jprofile(request):
   return render(request, "jprofile.html")
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

        
        return render(request, "calendarCandidate.html", {'data': "[]" if row.calendar == "" else row.calendar, 'uid': request.GET['id']})

@csrf_exempt
def calendar(request):
    if request.method == 'GET':
        id = request.GET["id"]
        if id == "":
            return HttpResponse("Invalid Request")
        row = models.JobProfile.objects.get(jobId__exact=request.GET['id'])
        return render(request, "calendar.html", {'data': "[]" if row.calendar == "" else row.calendar, 'jobId': request.GET['id']})
    else:
        if request.POST['id'] != "":
            id = request.POST['id']
            row = models.JobProfile.objects.get(jobId__exact=id)
            row.calendar = request.POST['calendar']
            row.save()
        else:
            uid = request.POST['uid']
            user = models.Person.objects.get(stringId__exact=request.POST['uid'])
            id = user.questions
            row = models.JobProfile.objects.get(jobId__exact=id)
            newVal = request.POST['calendar']
            newVal = newVal.replace("#FFFFFF", "#FFA07A");
            row.calendar = row.calendar.replace(request.POST['calendar'], newVal, 1)
            row.save()
        return HttpResponse("success")

@csrf_exempt
def sendInterviewLink(request):
    candidates = request.POST.getlist('candidates[]')
    for i in candidates:
        print(i)
        candidate = models.Person.objects.get(mobile__exact=i)
        candidate.status = "Invited"
        url = "http://ec2-3-17-12-192.us-east-2.compute.amazonaws.com/calendarCandidate?id=" + candidate.stringId
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
    url = "http://ec2-3-17-12-192.us-east-2.compute.amazonaws.com/getLink?linkId=" + row.linkId
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


    return render(request,"getLink.html",{'linkId':linkId})

@csrf_exempt
def saveJob(request):
    print("save")
    salary = request.POST['salary'].split('-')
    exp = request.POST['exp'].split('-')
    notice = request.POST['notice'].split('-')

    job = models.JobProfile(jobId=request.POST['jobid'], designation=request.POST['designation'], experience = request.POST['exp'], salary = request.POST['salary'], notice = request.POST['notice'], skills = request.POST['skills'], salary1 = salary[0], salary2 = salary[1], exp1 = exp[0], exp2 = exp[1], notice1 = notice[0], notice2 = notice[1], emails=request.POST['emails'])
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
        return render(request,"upload.html",{'form':student, 'jobIdList':jobIdList})

def index(request):  
    if request.method == 'POST': 
        student = StudentForm(request.POST, request.FILES)
        if student.is_valid():
            handle_uploaded_file(request.FILES['file'])  
            return HttpResponse("File uploaded successfuly")  
    else: 
        jobIdList = list(models.JobProfile.objects.order_by().values_list('jobId', flat=True).distinct())
        student = StudentForm()
        return render(request,"index.html",{'form':student, 'jobIdList':jobIdList})    

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
        data.status = "Received"
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
            score += GetScore(int(weightPerQuestion), q.expected1, q.expected2, data.experience)
        
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
        data.save()

        row.interestedCount += 1
        row.save()

        return HttpResponse("Data submitted successfuly" + request.POST['strId'])
    else:
        id = request.GET["id"]
        if id == "":
            return HttpResponse("Invalid Request")
        try:
            print(id)
            data = models.Person.objects.only('questions').get(stringId__exact=id)
        except models.Person.DoesNotExist:
            return HttpResponse("Invalid Request")

        row = models.JobProfile.objects.only('skills').get(jobId__exact=data.questions)
        skillList = []
        for x in row.skills.split(','):
            skillList.append(x)

        data.nextReminderTimestamp = int(time.time()) + 86400
        data.save()

        return render(request,"questions.html", {'qs': skillList, 'stringId': id})

def opt_out(request):
    if request.method == 'POST': 
        print('Receieved POST opt-out request for: ', request.POST["strId"])
        candidate = models.Person.objects.only('questions').filter(stringId__exact=request.POST['strId'])
        if candidate:
            candidate.delete()
            jobStats = models.JobProfile.objects.get(jobId__exact=candidate.questions)
            jobStats.optedOutCount += 1
            jobStats.save()
            return HttpResponse("You have successfuly opted-out")
        else:
            return HttpResponse("Invalid Request")
    else:
        print('Receieved GET opt-out request for: ', request.GET["id"])
        return render(request,"optout.html", {'stringId': request.GET["id"]})


def homepage(request):
    return HttpResponse("First App")

def clientSettings(request):
    settings = models.JobSettings.objects.get(companyId__exact="1")
    if settings:
        return render(request, "settings.html", { "jobSettings": settings })
    else:
        return render(request, "settings.html", { "jobSettings": models.JobSettings() })

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
            data.answer2 = request.POST.get('answer2')
            data.answer3 = request.POST.get('answer3')
            data.save()
            q4 = models.OnlineTestKeys.objects.get(qid=data.question4)
            res = zip([['4',q4.type,q4.question,q4.choice1,q4.choice2,q4.choice3,q4.choice4,data.answer4]])
            return render(request,"onlinetest.html", {'qs': res, 'stringId': request.POST['strId']})
        elif request.POST.get("answer4") is not None:
            data.answer4 = request.POST.get('answer4')
            data.save()
            q5 = models.OnlineTestKeys.objects.get(qid=data.question5)
            res = zip([['5',q5.type,q5.question,q5.choice1,q5.choice2,q5.choice3,q5.choice4,data.answer5]])
            return render(request,"onlinetest.html", {'qs': res, 'stringId': request.POST['strId']})
        elif request.POST.get("answer5") is not None:
            data.status = "Received"
            data.answer5 = request.POST.get('answer5')
            data.onlinetestcomplete = 1
            data.save()
            return HttpResponse("Answers submitted successfuly" + data.answer1 + data.answer2 + data.answer3 + data.answer4 + data.answer5)
        else:
            #data.onlinetestcomplete == 1
            return HttpResponse("Timed out")
    else:
        id = request.GET["id"]
        if id == "":
            return HttpResponse("Invalid Request")
        try:
            print(id)
            data = models.Person.objects.only('questions').get(stringId__exact=id)  
            #if data.onlinetestcomplete == 1:
            #    return HttpResponse("<h3>Online test submitted already.<h3>")            
            q1 = models.OnlineTestKeys.objects.get(qid=data.question1)
            q2 = models.OnlineTestKeys.objects.get(qid=data.question2)
            q3 = models.OnlineTestKeys.objects.get(qid=data.question3)	
            res = zip([['1', q1.type,q1.question,q1.choice1,q1.choice2,q1.choice3,q1.choice4,data.answer1],['2',q2.type,q2.question,q2.choice1,q2.choice2,q2.choice3,q2.choice4,data.answer2],['3',q3.type,q3.question,q3.choice1,q3.choice2,q3.choice3,q3.choice4,data.answer3]])
            return render(request,"onlinetest.html", {'qs': res, 'stringId': id})
        except models.Person.DoesNotExist:
            return HttpResponse("Invalid Request")

# Create your views here.
