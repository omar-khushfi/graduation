from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'exam'
urlpatterns = [
   
    path('<int:lan>',views.ExamView.as_view(),name="exam"),  
    path('create_exam',views.CreateExamView.as_view(),name="create_exam"),  
]