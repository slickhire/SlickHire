from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=30)
    mobile = models.CharField(max_length=30, primary_key=True)
    experience = models.CharField(max_length=30)
    institute = models.CharField(max_length=30)
    education = models.CharField(max_length=30)
    employer = models.CharField(max_length=30)
    skills = models.CharField(max_length=30)
    score = models.CharField(max_length=30)
    salary = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    status = models.CharField(max_length=30)
    stringId = models.CharField(max_length=30, db_index=True)
    questions = models.CharField(max_length=30)
    reminderscount = models.IntegerField(default=0)
# Create your models here.
class Questions(models.Model):
    key = models.CharField(max_length=30)
    q = models.CharField(max_length=30)
    options = models.CharField(max_length=30)
    tagId = models.CharField(max_length=30)
    expected1 = models.CharField(max_length=30)
    expected2 = models.CharField(max_length=30)

class JobProfile(models.Model):
    jobId = models.CharField(max_length=30, primary_key=True)
    designation = models.CharField(max_length=30)
    experience = models.CharField(max_length=30)
    salary = models.CharField(max_length=30)
    notice = models.CharField(max_length=30)
    skills = models.CharField(max_length=30)
    salary1 = models.CharField(max_length=30)
    salary2 = models.CharField(max_length=30)
    notice1 = models.CharField(max_length=30)
    notice2 = models.CharField(max_length=30)
    exp1 = models.CharField(max_length=30)
    exp2 = models.CharField(max_length=30)
    calendar = models.CharField(max_length=5000)

class JobSettings(models.Model):
	companyId = models.CharField(max_length=30, primary_key=True)
	smsEnabled = models.BooleanField(default=False)
	whatsappEnabled = models.BooleanField(default=False)
	emailEnabled = models.BooleanField(default=False)
	voiceEnabled = models.BooleanField(default=False)
	remindersCount = models.IntegerField(default=0)
	onlineExamEnabled = models.BooleanField(default=False)
