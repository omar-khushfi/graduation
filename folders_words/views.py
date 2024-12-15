from datetime import timedelta
import json
from django.http import JsonResponse
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

from pro import settings
from .models import *
import requests
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from gtts import gTTS
import os
import re

from django.views.decorators.http import require_POST

def translate_text_mymemory(source_text, source_lang, target_lang):
    url = f"https://api.mymemory.translated.net/get?q={source_text}&langpair={source_lang}|{target_lang}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()['responseData']['translatedText']
    else:
        return "Error: Could not translate."

def generate_pronunciation(word, language, user_id):
    sanitized_word = re.sub(r'[\\/*?:"<>|]', '', word)
    language_code = language.type
    save_path = os.path.join(
        settings.MEDIA_ROOT, 
        "voices", 
        f"user_{user_id}", 
        language_code, 
        f"{sanitized_word}_{language_code}.mp3"
    )
    print(f"Save path: {save_path}")
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
    except Exception as e:
        print(f"Error creating directories: {e}")
        return None
    try:
        tts = gTTS(text=word, lang=language_code)
        tts.save(save_path)
        return f"voices/user_{user_id}/{language_code}/{sanitized_word}_{language_code}.mp3"
    except Exception as e:
        print(f"Error generating pronunciation for {word}: {e}")
        return None

##################################################

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
        user=request.user
        folder=get_object_or_404(Folder,pk=pk)
        languages=Language.objects.filter(user=user)
        words=Word.objects.filter(folder=folder,user=user)
        main_lang=Language.objects.get(user=user,Is_Native=True)
        all_translate=[]
        if Word.objects.all().count()>0:
            for wo in words:
                word=[]
                for la in languages:
                    qyword=""
                    
                    if Translate.objects.filter(language=la,word=wo,user=user).exists():
                        qyword=Translate.objects.get(language=la,word=wo,user=user)
                    else:
                        
                        nativ_trans=Translate.objects.get(user=user,word=wo,language=main_lang)

                        translated = translate_text_mymemory(nativ_trans.word.content, nativ_trans.language.type, la.type)
                        voice_path = generate_pronunciation(translated, la, user.id)       
                        
                        qyword=Translate.objects.create(language=la,word=wo,user=user,translation=translated, voice=voice_path)
                    word.append(qyword)
                all_translate.append(word)
                
        
        context={
            'folder':folder,
            'translates':all_translate,
            'languages':languages
        }
        return render(request,'folder.html',context)
    
    
 
 
 


class add_word(View):
    def get(self,request,pk):
        folder=get_object_or_404(Folder,pk=pk)
        return render(request,'enter_word.html')
    def post(self,request,pk):
        word=request.POST.get('word')
        
        user=request.user
        folder=get_object_or_404(Folder,pk=pk)
        languages=Language.objects.filter(user=user)
      
        main_lang=Language.objects.get(user=user,Is_Native=True)
        new_word=Word.objects.create(content=word,user=user,folder=folder)

        for language in languages:
            translated=""
            if language != main_lang:
                try:
                    translated = translate_text_mymemory(word, main_lang.type, language.type)
                except:
                    translated=""
            else:
                translated=word
           
            voice_path = generate_pronunciation(translated, language, user.id)
            Translate.objects.create(user=user, language=language, word=new_word, translation=translated, voice=voice_path)
        
        return render(request,'enter_word.html')
    
    
# الإنجليزية (en)
# الإسبانية (es)
# الفرنسية (fr)
# الألمانية (de)
# الإيطالية (it)
# البرتغالية (pt)
# الروسية (ru)
# العربية (ar)
# الصينية المبسطة (zh)
# اليابانية (ja)
# الكورية (ko)
# الهولندية (nl)
# البولندية (pl)
# السويدية (sv)
# الدنماركية (da)
# النرويجية (no)
# الفيتنامية (vi)
# التشيكية (cs)
# التركية (tr)
# اليونانية (el)
# الهنغارية (hu)
# الفلمنكية (nl)
# الرومانية (ro)
# السلوفينية (sl)
# السلوفاكية (sk)
# الكرواتية (hr)
# البلغارية (bg)
# الإستونية (et)
# اللتوانية (lt)
# المالطية (mt)
# الأوكرانية (uk)
# الفلبينية (tl)


class edit_word(View):
    def get(self,request,pk,id):
        user=request.user
        word=get_object_or_404(Word,id=id)
        translates=Translate.objects.filter(word=word,user=user)
        languages=Language.objects.filter(user=user)
        
        context={
            'word':word,
            'translates':translates,
             'languages':languages
        }
        return render(request,"edit_word.html",context)        
    def post(self,request,pk,id):
        user=request.user
        items=request.POST.items()
        for key,value in items:
            if value!="" and key.startswith("translate_"):
                new_key=key[10:]
                try:
                    translate=Translate.objects.get(id=new_key)
                    translate.translation=value
                    voice_path = generate_pronunciation(translate.translation, translate.language, user.id)
                    translate.voice=voice_path
                    translate.save()
                except:
                    pass
        return redirect(f'/folder/{pk}')        


def delete_word(request, pk, word_id):
    word = get_object_or_404(Word, pk=word_id)
    word.delete()
    return JsonResponse({'success': True})

def delete_selected_words(request):
    try:
        data = json.loads(request.body)  
        word_ids = data.get('word_ids', [])
        Word.objects.filter(id__in=word_ids).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})