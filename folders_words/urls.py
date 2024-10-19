from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
  
   path('',views.folders.as_view(),name="folders"),
   path('folder/<int:pk>',views.folder.as_view(),name="folder"),
    
]
