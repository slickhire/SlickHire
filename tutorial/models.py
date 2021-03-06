from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

#class Person(models.Model):
class Person(ExportModelOperationsMixin('candidate'), models.Model):
    checkbox = models.CharField(max_length=1, default="")
    name = models.CharField(max_length=30)
    mobile = models.CharField(max_length=30, primary_key=True)
    institute = models.CharField(max_length=30)
    education = models.CharField(max_length=30)
    employer = models.CharField(max_length=30)
    skills = models.CharField(max_length=30)
    score = models.CharField(max_length=30)
    salary = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    status = models.CharField(max_length=30)
    onlinetestscore = models.IntegerField(default=0)
    experience = models.CharField(max_length=30)
    expectedCtc = models.CharField(max_length=30, default="")
    notice = models.CharField(max_length=30, default="")
    stringId = models.CharField(max_length=30, db_index=True)
    questions = models.CharField(max_length=30)
    reminderscount = models.IntegerField(default=0)
    nextReminderTimestamp = models.IntegerField(default=0)
    onlinetesteval = models.IntegerField(default=-1)
    onlinetestcompileerrors = models.IntegerField(default=0)
    onlinetestcomplete = models.IntegerField(default=0)
    question1 = models.IntegerField(default=0)
    question2 = models.IntegerField(default=0)
    question3 = models.IntegerField(default=0)
    question4 = models.IntegerField(default=0)
    question5 = models.IntegerField(default=0)
    answer1 = models.TextField(default="0")
    answer2 = models.TextField(default="0")
    answer3 = models.TextField(default="0")
    answer4 = models.TextField(default="0")
    answer5 = models.TextField(default="0")
    onlinePrefProgLang = models.TextField(default="python")
    onlineProgLangCM = models.TextField(default="python")
    onlineProgLangIDE =  models.TextField(default="Python")
    onlineStartTimeStamp = models.IntegerField(default=0)
    onlineAnswer1Time = models.IntegerField(default=0)
    onlineAnswer2Time = models.IntegerField(default=0)
    onlineAnswer3Time = models.IntegerField(default=0)
    onlineAnswer4Time = models.IntegerField(default=0)
    onlineAnswer5Time = models.IntegerField(default=0)
    calendar = models.CharField(max_length=30, default = "")
    statusTimestamp = models.IntegerField(default=0)
    onlineTestTimePending = models.IntegerField(default=3600)
    currentOnlineQuestion = models.IntegerField(default=1)
    

#class JobProfile(models.Model):
class JobProfile(ExportModelOperationsMixin('jobprofile'), models.Model):
    jobId = models.CharField(max_length=100, primary_key=True)
    designation = models.CharField(max_length=30)
    experience = models.CharField(max_length=30)
    salary = models.CharField(max_length=30)
    notice = models.CharField(max_length=30)
    skills = models.CharField(max_length=30)
    emails = models.CharField(max_length=100)
    salary1 = models.CharField(max_length=30)
    salary2 = models.CharField(max_length=30)
    notice1 = models.CharField(max_length=30)
    onlineProgExamCategory = models.TextField(default="none")
    onlinePrefProgLang = models.TextField(default="any")
    onlinePassPercentage = models.IntegerField(default=100)
    notice2 = models.CharField(max_length=30)
    exp1 = models.CharField(max_length=30)
    exp2 = models.CharField(max_length=30)
    calendar = models.CharField(max_length=5000)
    onlineProgExamPendingCount = models.IntegerField(default=0)
    onlineProgExamDoneCount = models.IntegerField(default=0)
    question1 = models.IntegerField(default=0)
    question2 = models.IntegerField(default=0)
    question3 = models.IntegerField(default=0)
    question4 = models.IntegerField(default=0)
    question5 = models.IntegerField(default=0)
    availSlots = models.CharField(max_length=5000, default="")
    lastEventId = models.IntegerField(default=1)

class JobSettings(models.Model):
	companyId = models.CharField(max_length=30, primary_key=True)
	smsEnabled = models.BooleanField(default=False)
	whatsappEnabled = models.BooleanField(default=False)
	emailEnabled = models.BooleanField(default=False)
	voiceEnabled = models.BooleanField(default=False)
	remindersCount = models.IntegerField(default=0)

class InternalLink(models.Model):
    linkId = models.CharField(max_length=30, primary_key=True)
    candidates = models.CharField(max_length=500)
	
# Model answer keys and testcases for programs
# type of question include "CHOICE" (1) , "PROGRAM"(0)
# format for question is string. example: "Write a sample program to 
# determine whether input is a leap year or not"
# Test format is: format is inputs;outputs
# example "2 3;5" here 2 and 3 are inputs and 5 is the expected output
class OnlineTestKeys(models.Model):
    qid = models.IntegerField(primary_key=True)
    type = models.IntegerField()
    category = models.TextField()
    question = models.TextField()
    choice1 = models.TextField()
    choice2 = models.TextField()
    choice3 = models.TextField()
    choice4 = models.TextField()
    answer = models.TextField()
    test1 = models.TextField() 
    test2 = models.TextField()
    test3 = models.TextField()
    test4 = models.TextField()
    test5 = models.TextField()

# Status is in JSON format as below:
# [
#    {
#       "jobId": "<ID>",
#       "state": "<Candidate State>",
#       "stateTimestamp": "<Timestamp>"
#       "reason": "<Reason>"
#    },
#    .....
# ]
#class CandidateHistory(models.Model):
class CandidateHistory(ExportModelOperationsMixin('CandidateHistory'), models.Model):
    mobile = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    entryTime = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=8096, default="[]")
