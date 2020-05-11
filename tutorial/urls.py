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
from .integrator import CallHandler
from .integrator import StartQuestionaireReminder
urlpatterns = [
    path('index/', views.index),
    path('index/data/', views.data),
    path('questions', views.questions),
    path('opt_out', views.opt_out),
    path('jprofile',views.jprofile),
    path('jprofile/save_job/', views.saveJob),
    path('jprofile/get_job/', views.getJob),
    path('jprofile/delete_job/', views.deleteJob),
    path('calendar', views.calendar),
    path('calendarCandidate', views.calendarCandidate),
    path('',views.homepage, name="homepage"),
    path('settings', views.settings),
    path('settings/job', views.jobSettings)
]

CallHandler()
StartQuestionaireReminder(repeat=5, repeat_until=None)
