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

# Create your models here.
class Questions(models.Model):
    key = models.CharField(max_length=30)
    q = models.CharField(max_length=30)
    options = models.CharField(max_length=30)
    tagId = models.CharField(max_length=30)
    expected1 = models.CharField(max_length=30)
    expected2 = models.CharField(max_length=30)
