from django.shortcuts import render
from django.http import HttpResponse
from tutorial.functions import handle_uploaded_file  
from tutorial.forms import StudentForm  
from django.core.serializers import serialize
from django.http import JsonResponse
from . import models

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
    #print(JsonResponse({'data': data}), safe=False)
    #data = [{'id': 1, 'name': 'xyz', 'mobile': '888', 'experience': '', 'institute': '', 'education': '', 'employer': '', 'skills': '', 'score': '', 'salary': '1', 'email': '', 'status': '2'}]
  #  data = [['id': '1', "name": "xyz", "mobile": "888", "experience": "", "institute": "", "education": "", "employer": "", "skills": "", "score": "", "salary": "1", "email": "", "status": "2"]]
    #return JsonResponse(data, safe=False)
    return JsonResponse({"draw": 1, "recordsTotal": 1, "recordsFiltered": 1, "data": data}, safe=False)
    #return JsonResponse(serialize('json', list(models.Person.objects.values()), safe=False))#, cls=LazyEncoder))

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
        questions = models.Questions.objects.filter(key__exact=data.questions)
        score = 0
        for q in questions:
            print("hello", q.tagId)
            if request.POST[q.tagId] != "":
                if q.tagId == "experience":
                    data.experience = request.POST[q.tagId]
                    if int(q.expected1) <= int(data.experience) <= int(q.expected2):
                        score += 50
                    else:
                        score += GetScore(int(50), q.expected1, q.expected2, data.experience)  
                if q.tagId == "company":
                    data.employer = request.POST[q.tagId]
                if q.tagId == "currentCtc":
                    data.salary = request.POST[q.tagId]
                if q.tagId == "expectedCtc":
                    data.expectedCtc = request.POST[q.tagId]
                    data.salary = data.expectedCtc
                    if int(q.expected1) <= int(data.expectedCtc) <= int(q.expected2):
                        score += 50
                    elif int(q.expected1) > int(data.expectedCtc) :
                        score += 50
                    else:
                        score += GetScore(int(50), q.expected1, q.expected2, data.expectedCtc) 
        data.score = score
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
            return HttpResponse("Invalid Request")

        return render(request,"questions.html", {'qs': list(models.Questions.objects.filter(key__exact=data.questions)), 'stringId': id})


def homepage(request):
    return HttpResponse("First App")

# Create your views here.
