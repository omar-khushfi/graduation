import json
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from pro import settings
from .models import *
import requests
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from gtts import gTTS
import os
import re
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .models import Folder, Word, Translate
import arabic_reshaper
from bidi.algorithm import get_display
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

def translate_text_mymemory(source_text, source_lang, target_lang):
    url = f"https://api.mymemory.translated.net/get?q={source_text}&langpair={source_lang}|{target_lang}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()['responseData']['translatedText']
    else:
        return "Error: Could not translate."
def generate_pronunciation(word, language, user_id):
    sanitized_word = re.sub(r'[\\/*?:"<>|]', '', word)
    language_code = language.code
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

class folders(LoginRequiredMixin,View):
    login_url = 'account/login/'  
    
    def get(self,request):
        user=request.user
        folders=Folder.objects.filter(user=user.id)
        
        paginator=Paginator(folders,8) 
        page_number=request.GET.get("page")
        try:
            folders=paginator.page(page_number)
        except PageNotAnInteger: 
            folders=paginator.page(1)
        except EmptyPage: 
            folders=paginator.page(1)

        context={
            'folders':folders,
            'user':user
        }
        print(user.theme)
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
        paginator=Paginator(folders,8) 
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
    
    
class folder(LoginRequiredMixin,View):
    login_url = 'account/login/'  

    def post(self,request,pk):
       pass
    def get(self,request,pk):
        user=request.user
        folder=get_object_or_404(Folder,pk=pk)
        languages=Language.objects.filter(user=user)
        words=Word.objects.filter(folder=folder,user=user)
        main_lang=Language.objects.get(user=user,is_native=True)
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
                        translated = translate_text_mymemory(nativ_trans.word.content, nativ_trans.language.code, la.code)
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
    
    
 
 
 


class AddWordView(LoginRequiredMixin, View):
    login_url = '/account/login/'

    def get(self,request,pk):
        folder=get_object_or_404(Folder,pk=pk)
        return render(request,'enter_word.html')
    def post(self,request,pk):
        word=request.POST.get('word')
        
        user=request.user
        folder=get_object_or_404(Folder,pk=pk)
        languages=Language.objects.filter(user=user)
      
        main_lang=Language.objects.get(user=user,is_native=True)
        new_word=Word.objects.create(content=word,user=user,folder=folder)

        for language in languages:
            translated=""
            if language != main_lang:
                try:
                    translated = translate_text_mymemory(word, main_lang.code, language.code)
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


class edit_word(LoginRequiredMixin,View):
    login_url = 'account/login/'  

    def get(self,request,pk,id):
        user=request.user
        word=get_object_or_404(Word,id=id)
        translates=Translate.objects.filter(word=word,user=user)
        languages=Language.objects.filter(user=user)
        
        # Debug print statements
        print("Debug: Translates count:", translates.count())
        print("Debug: Languages count:", languages.count())
        
        for translate in translates:
            print(f"Debug: Translate - Language: {translate.language}, Code: {translate.language.code}, Display: {translate.language.get_code_display()}")
        
        for language in languages:
            print(f"Debug: Language - Code: {language.code}, Display: {language.get_code_display()}")
        
        context={
            'word':word,
            'translates':translates,
            'languages':languages,
            'pk':pk
        }
        return render(request,"edit_word.html",context)
        
    def post(self,request,pk,id):
        user=request.user
        word=get_object_or_404(Word,id=id)
        items=request.POST.items()
        updated = False
        for key,value in items:
            if value!="" and key.startswith("translate_"):
                if "new_" in key:
                    # معالجة الترجمات الجديدة
                    lang_id = key.split("_")[-1]
                    try:
                        language = Language.objects.get(id=lang_id, user=user)
                        voice_path = generate_pronunciation(value, language, user.id)
                        Translate.objects.create(
                            user=user,
                            language=language,
                            word=word,
                            translation=value,
                            voice=voice_path
                        )
                        updated = True
                    except Exception as e:
                        print(f"Error creating new translation: {e}")
                else:
                    # تحديث الترجمات الموجودة
                    new_key=key[10:]
                    try:
                        translate=Translate.objects.get(id=new_key)
                        translate.translation=value
                        voice_path = generate_pronunciation(translate.translation, translate.language, user.id)
                        translate.voice=voice_path
                        translate.save()
                        updated = True
                    except Exception as e:
                        print(f"Error updating translation: {e}")
        if updated:
            messages.success(request, "تم تحديث الكلمة بنجاح")
        # استخدم str(pk) للتأكد من أن pk ليس فارغًا وأنه قيمة صالحة
        return redirect('folders_words:folder', pk=str(pk))        

@login_required
def delete_word(request, pk, word_id):
    word = get_object_or_404(Word, pk=word_id)
    word.delete()
    print(pk,word_id)
    return JsonResponse({'success': True})

@login_required
def delete_selected_words(request):
    try:
        data = json.loads(request.body)  
        word_ids = data.get('word_ids', [])
        Word.objects.filter(id__in=word_ids).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

from reportlab.lib.pagesizes import A4
from django.urls import reverse


@login_required
def generate_pdf(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{folder.name}_translations.pdf"'

    # استخدام حجم A4
    width, height = A4
    p = canvas.Canvas(response, pagesize=A4)

    # تحميل الخط العربي "Amiri" من ال��نترنت
    font_url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
    font_path = os.path.join(settings.MEDIA_ROOT, 'Amiri-Regular.ttf')

    if not os.path.exists(font_path):
        font_data = requests.get(font_url).content
        with open(font_path, 'wb') as f:
            f.write(font_data)

    # تسجيل الخط العربي
    pdfmetrics.registerFont(TTFont('Amiri', font_path))

    def format_arabic(text):
        return get_display(arabic_reshaper.reshape(text))

    # إضافة خلفية ملونة
    p.setFillColorRGB(0.95, 0.95, 1)  # لون أزرق فاتح جداً
    p.rect(0, 0, width, height, fill=1)

    # إضافة عنوان للمستند
    p.setFillColorRGB(0.2, 0.2, 0.6)  # لون أزرق داكن للعنوان
    p.setFont('Amiri', 24)
    title = format_arabic(f"ترجمات المجلد: {folder.name}")
    p.drawRightString(width - 50, height - 50, title)

    # إضافة خط أفقي تحت العنوان
    p.setStrokeColorRGB(0.2, 0.2, 0.6)
    p.line(50, height - 70, width - 50, height - 70)

    y_position = height - 100
    words = Word.objects.filter(folder=folder)

    for word in words:
        if y_position < 100:
            p.showPage()
            p.setFillColorRGB(0.95, 0.95, 1)
            p.rect(0, 0, width, height, fill=1)
            y_position = height - 50

        # رسم مربع خلفي للكلمة
        p.setFillColorRGB(0.9, 0.9, 1)  # لون أزرق فاتح جداً للخلفية
        p.roundRect(50, y_position - 10, width - 100, 40, 10, fill=1)

        p.setFillColorRGB(0.2, 0.2, 0.6)  # لون أزرق داكن للنص
        p.setFont('Amiri', 16)
        word_text = format_arabic(f"{word.content}")
        p.drawRightString(width - 60, y_position, word_text)
        y_position -= 30

        translations = Translate.objects.filter(word=word)
        for translation in translations:
            p.setFont('Amiri', 14)
            translation_text = format_arabic(f"{translation.translation} :{translation.language.code}")
            p.drawRightString(width - 70, y_position, translation_text)
            y_position -= 25

        y_position -= 20

    # إضافة رقم الصفحة
    p.setFont('Amiri', 10)
    p.drawRightString(width - 50, 30, str(p.getPageNumber()))

    p.showPage()
    p.save()

    return response


@login_required
def delete_folder(request, pk):
    folder = get_object_or_404(Folder, pk=pk)
    if folder.user != request.user:
        # Or some other appropriate error page
        return HttpResponseForbidden("You do not have permission to delete this folder.")
    folder.delete()
    return redirect(reverse('folders_words:folders'))
