from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from accounts.models import User
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from .models import *
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger



class folders(View):
    def get(self,request):
        user=request.user
        folders=Folder.objects.filter(user=user.id)
        
        paginator=Paginator(folders,1) 
        page_number=request.GET.get("page")
        try:
            folders=paginator.page(page_number)
        except PageNotAnInteger: 
            folders=paginator.page(1)
        except EmptyPage: 
            folders=paginator.page(1)

        context={
            'folders':folders
        }
        return render(request,'folders.html',context)
    def post(self,request):
        user=request.user
        if request.POST.get("new_folder"):
            new_folder=request.POST.get("new_folder")
            
            user=request.user
            if Folder.objects.filter(name=new_folder).exists():
                messages.error(request,"this folder is already exists ")
            else:
                folder=Folder.objects.create(name=new_folder,user=user)
        
        
        
        folders=Folder.objects.filter(user=user.id)
        paginator=Paginator(folders,1) 
        page_number=request.GET.get("page")
        try:
            folders=paginator.page(page_number)
        except PageNotAnInteger: 
            folders=paginator.page(1)
        except EmptyPage: 
            folders=paginator.page(1)

        context={
            'folders':folders
        }
        return render(request,'folders.html',context)
    
    
class folder(View):
    def post(self,request,pk):
       pass
    def get(self,request,pk):
        folder=get_object_or_404(Folder,pk=pk)
        words=Word.objects.filter(folder=folder)
        context={
            'folder':folder,
            'words':words
        }
        return render(request,'folder.html',context)