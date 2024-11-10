from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'exam'
urlpatterns = [
    # path('select_word/',views.select_word.as_view(),name="select_word")
    path('',views.exam.as_view(),name="exam"),    
]