"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from .functions import StartProcesses
urlpatterns = [
    path('index/', views.index),
    path('index/data/', views.data),
    path('upload/', views.upload),
    path('index/send_link/', views.sendLink),
    path('getLink', views.getLink),
    path('getLink/data/', views.getLinkData),
    path('getLink/send_interview_link/', views.sendInterviewLink),
    path('questions', views.questions),
    path('opt_out', views.opt_out),
    path('jprofile',views.jprofile),
    path('jprofile/save_job/', views.saveJob),
    path('jprofile/get_job/', views.getJob),
    path('jprofile/delete_job/', views.deleteJob),
    path('calendar', views.calendar),
    path('calendarCandidate', views.calendarCandidate),
    path('',views.homepage, name="homepage"),
    path('settings', views.clientSettings),
    path('settings/job', views.jobSettings),
    path('online', views.online),
    path('add_questions', views.add_questions),
    path('printPersons', views.printPersons),
    path('printquestions',views.printquestions) 
]

StartProcesses()
