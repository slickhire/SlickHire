from django.shortcuts import render
from django.http import HttpResponse
from tutorial.functions import handle_uploaded_file  
from tutorial.forms import StudentForm  
from django.core.serializers import serialize
from django.http import JsonResponse
from . import models
from django.views.decorators.csrf import csrf_exempt
import json

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
def saveJob(request):
    print("save")
    salary = request.POST['salary'].split('-')
    exp = request.POST['exp'].split('-')
    notice = request.POST['notice'].split('-')

    job = models.JobProfile(jobId=request.POST['jobid'], designation=request.POST['designation'], experience = request.POST['exp'], salary = request.POST['salary'], notice = request.POST['notice'], skills = request.POST['skills'], salary1 = salary[0], salary2 = salary[1], exp1 = exp[0], exp2 = exp[1], notice1 = notice[0], notice2 = notice[1])
    job.save()

    return HttpResponse("success")

def index(request):  
    if request.method == 'POST': 
        student = StudentForm(request.POST, request.FILES)
        if student.is_valid():
            handle_uploaded_file(request.FILES['file'])  
            return HttpResponse("File uploaded successfuly")  
    else: 
        student = StudentForm()
        return render(request,"index.html",{'form':student})    

def data(request):
    data = list(models.Person.objects.values_list())
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

def settings(request):
    return render(request, "settings.html")

def jobSettings(request):
	config = models.JobSettings( \
				companyId="1",
               	smsEnabled=request.POST.get('sms', False),
				whatsappEnabled=request.POST.get('Whatsapp', False),
				emailEnabled=request.POST.get('email', False),
				voiceEnabled=request.POST.get('voice', False),
				onlineExamEnabled=request.POST.get('onlineProg', False),
				remindersCount=request.POST.get('remindCount', 0))
	config.save()
	return HttpResponse("Settings Saved")

# Create your views here.
