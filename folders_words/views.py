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
from datetime import datetime
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
    
    
class folder(LoginRequiredMixin, View):
    login_url = 'account/login/'  

    def post(self, request, pk):
        pass

    def get(self, request, pk):
        user = request.user
        folder = get_object_or_404(Folder, pk=pk)
        languages = Language.objects.filter(user=user)
        words = Word.objects.filter(folder=folder, user=user)
        main_lang = Language.objects.get(user=user, is_native=True)

        # --- pagination ---
        page_number = request.GET.get("page")
        paginator = Paginator(words, 9)  
        page_obj = paginator.get_page(page_number)
        words_page = page_obj.object_list

        all_translate = []
        if words_page.count() > 0:
            for wo in words_page:
                word = []
                for la in languages:
                    qyword = ""
                    if Translate.objects.filter(language=la, word=wo, user=user).exists():
                        qyword = Translate.objects.get(language=la, word=wo, user=user)
                    else:
                        nativ_trans = Translate.objects.get(user=user, word=wo, language=main_lang)
                        translated = translate_text_mymemory(
                            nativ_trans.word.content,
                            nativ_trans.language.code,
                            la.code
                        )
                        voice_path = generate_pronunciation(translated, la, user.id)       
                        qyword = Translate.objects.create(
                            language=la, word=wo, user=user,
                            translation=translated, voice=voice_path
                        )
                    word.append(qyword)
                all_translate.append(word)

        context = {
            'folder': folder,
            'translates': all_translate,
            'languages': languages,
            'page_obj': page_obj,
        }
        return render(request, 'folder.html', context)
 
 


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
    


class edit_word(LoginRequiredMixin,View):
    login_url = 'account/login/'  

    def get(self,request,pk,id):
        user=request.user
        word=get_object_or_404(Word,id=id)
        translates=Translate.objects.filter(word=word,user=user)
        languages=Language.objects.filter(user=user)
        
     
        
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
            messages.success(request, "The word has been updated successfully.")
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
    
    width, height = A4
    p = canvas.Canvas(response, pagesize=A4)
    
    # Use the original font loading code without changes
    font_url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
    font_path = os.path.join(settings.MEDIA_ROOT, 'Amiri-Regular.ttf')
    
    if not os.path.exists(font_path):
        font_data = requests.get(font_url).content
        with open(font_path, 'wb') as f:
            f.write(font_data)
    
    pdfmetrics.registerFont(TTFont('Amiri', font_path))
    
    def format_arabic(text):
        return get_display(arabic_reshaper.reshape(text))
    
    def center_text(p, text, font_name, font_size, x_center, y):
        """Helper function to center text at given x position"""
        text_width = p.stringWidth(text, font_name, font_size)
        x_pos = x_center - (text_width / 2)
        p.drawString(x_pos, y, text)
    
    # Get all words and their translations
    words = Word.objects.filter(folder=folder)
    
    # Get all unique languages used in this folder
    languages = []
    for word in words:
        word_languages = Translate.objects.filter(word=word).select_related('language').distinct()
        for translate in word_languages:
            lang_code = translate.language.code
            lang_name = translate.language.get_code_display()
            if lang_code not in [l[0] for l in languages]:
                languages.append((lang_code, lang_name))
    
    # Table settings
    margin = 40
    table_width = width - (2 * margin)
    row_height = 35
    header_height = 50
    
    # Calculate column widths
    if languages:
        original_col_width = table_width * 0.3  # 30% for original word
        trans_col_width = (table_width * 0.7) / len(languages)  # 70% divided among languages
    else:
        original_col_width = table_width
        trans_col_width = 0
    
    def draw_page_header(p, page_num):
        """Draw page title and number"""
        # Page title
        p.setFillColorRGB(0.1, 0.1, 0.4)
        p.setFont('Amiri', 20)
        title = format_arabic(f" {folder.name}")
        p.drawRightString(width - margin, height - 30, title)
        
        # Page number
        p.setFont('Amiri', 10)
        page_text = format_arabic(f"{page_num}")
        p.drawString(margin, height - 30, page_text)
        
        # Divider line
        p.setStrokeColorRGB(0.3, 0.3, 0.6)
        p.setLineWidth(1)
        p.line(margin, height - 45, width - margin, height - 45)
    
    def draw_table_header(p, y_pos):
        """Draw table header with language names"""
        # Header background
        p.setFillColorRGB(0.2, 0.3, 0.6)
        p.rect(margin, y_pos - header_height, table_width, header_height, fill=1)
        
        # Header border
        p.setStrokeColorRGB(0.1, 0.1, 0.3)
        p.setLineWidth(2)
        p.rect(margin, y_pos - header_height, table_width, header_height, fill=0)
        
        # Column headers
        p.setFillColorRGB(1, 1, 1)  # White text
        p.setFont('Amiri', 14)
        
        # Original word column header
        original_header = format_arabic("original word")
        p.drawRightString(margin + original_col_width - 10, y_pos - 25, original_header)
        
        # Language column headers
        x_pos = margin + original_col_width
        for lang_code, lang_name in languages:
            # Vertical divider
            p.setStrokeColorRGB(0.4, 0.4, 0.7)
            p.setLineWidth(1)
            p.line(x_pos, y_pos - header_height, x_pos, y_pos)
            
            # Language name - centered using helper function
            lang_text = format_arabic(lang_name if lang_name else lang_code)
            center_text(p, lang_text, 'Amiri', 14, x_pos + trans_col_width/2, y_pos - 25)
            x_pos += trans_col_width
        
        return y_pos - header_height
    
    def draw_table_row(p, word, y_pos, row_num):
        """Draw a single table row"""
        # Alternating row colors
        if row_num % 2 == 0:
            p.setFillColorRGB(0.97, 0.97, 1)
        else:
            p.setFillColorRGB(0.92, 0.92, 0.98)
        
        p.rect(margin, y_pos - row_height, table_width, row_height, fill=1)
        
        # Row border
        p.setStrokeColorRGB(0.7, 0.7, 0.8)
        p.setLineWidth(0.5)
        p.rect(margin, y_pos - row_height, table_width, row_height, fill=0)
        
        # Original word
        p.setFillColorRGB(0.1, 0.1, 0.4)
        p.setFont('Amiri', 12)
        word_text = format_arabic(word.content)
        p.drawRightString(margin + original_col_width - 10, y_pos - 22, word_text)
        
        # Translations
        x_pos = margin + original_col_width
        translations_dict = {}
        
        # Get all translations for this word
        word_translations = Translate.objects.filter(word=word)
        for trans in word_translations:
            translations_dict[trans.language.code] = trans.translation
        
        for lang_code, lang_name in languages:
            # Vertical divider
            p.setStrokeColorRGB(0.7, 0.7, 0.8)
            p.setLineWidth(0.5)
            p.line(x_pos, y_pos - row_height, x_pos, y_pos)
            
            # Translation text
            if lang_code in translations_dict:
                p.setFillColorRGB(0.2, 0.4, 0.2)
                p.setFont('Amiri', 11)
                trans_text = format_arabic(translations_dict[lang_code])
                # Center the text in the column using helper function
                center_text(p, trans_text, 'Amiri', 11, x_pos + trans_col_width/2, y_pos - 22)
            else:
                # Empty cell marker - centered using helper function
                p.setFillColorRGB(0.6, 0.6, 0.6)
                p.setFont('Amiri', 11)
                empty_text = "-"
                center_text(p, empty_text, 'Amiri', 11, x_pos + trans_col_width/2, y_pos - 22)
            
            x_pos += trans_col_width
        
        return y_pos - row_height
    
    # Start generating PDF
    y_position = height - 60
    page_number = 1
    row_count = 0
    
    # Draw first page header
    draw_page_header(p, page_number)
    
    # Draw table header
    y_position = draw_table_header(p, y_position)
    
    # Draw data rows
    for word in words:
        # Check if we need a new page
        if y_position - row_height < 50:
            p.showPage()
            page_number += 1
            y_position = height - 60
            
            # Draw page header for new page
            draw_page_header(p, page_number)
            
            # Draw table header on new page
            y_position = draw_table_header(p, y_position)
            row_count = 0  # Reset for alternating colors
        
        # Draw the row
        y_position = draw_table_row(p, word, y_position, row_count)
        row_count += 1
    
    # Final table border
    p.setStrokeColorRGB(0.1, 0.1, 0.3)
    p.setLineWidth(2)
    p.line(margin, y_position, width - margin, y_position)
    
    p.showPage()
    p.save()
    
    return response



@login_required
def delete_folder(request, pk):
    folder = get_object_or_404(Folder, pk=pk)
    if folder.user != request.user:
        return HttpResponseForbidden("You do not have permission to delete this folder.")
    folder.delete()
    return redirect(reverse('folders_words:folders'))
