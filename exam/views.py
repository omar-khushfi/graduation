import datetime
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View
from .models import *
from datetime import datetime, timedelta


# Create your views here.



class exam(View):
    def get(self, request):
        user = request.user
        data = request.GET
        lang = data.get("lang")
        lang = Language.objects.get(id=1)
      
        now = datetime.now()
        exam = Exam.objects.filter(user=user, language=lang, end__gt=now, finish=False).first()

        if not exam:  
            exam = Exam.objects.create(
                user=user,
                language=lang,
                end=datetime.now() + timedelta(seconds=15),
            )
            words = Word.objects.filter(study=False).order_by('?')[:15]
            for word in words:
                Word_Exam.objects.create(user=user, word=word, exam=exam)
        
       
        word_exam = Word_Exam.objects.filter(exam=exam, done=False).first()

        if not word_exam: 
            exam.finish = True
            exam.save()
            return redirect(reverse("folders_words:folders"))
        
      
        true_translate = Translate.objects.get(user=user, word=word_exam.word, language=lang)
        false_translations = list(Translate.objects.filter(user=user, language=lang).exclude(word=word_exam.word)[:2])
        native_translate=Translate.objects.get(user=user,language__Is_Native=True,word=word_exam.word)
       
        words_with_translate = {
            'true': true_translate,
            'false1': false_translations[0] if len(false_translations) > 0 else None,
            'false2': false_translations[1] if len(false_translations) > 1 else None,
           
        }

        context = {
            'lang':lang.id,
            'exam': exam,
            'words_with_translate': words_with_translate,
            'current_word': word_exam.word,
             'native_translate':native_translate,
        }

        return render(request, "exam.html", context)
    
    def post(self, request):
        user = request.user
        data = request.POST
        lang = data.get("lang")
        word_id = data.get("current_word")
        selected_translation = data.get("ans")
        exam_id=data.get("exam")
        word=Word.objects.get(id=word_id)
        lang = Language.objects.get(id=lang)
        exam = Exam.objects.get(id=exam_id)
        print(selected_translation)
        if selected_translation.startswith("true"):
            Answer.objects.create(
                user=user,
                exam=exam,
                word=word,
                answer=selected_translation,
                is_true=True
            )
        else:
            Answer.objects.create(
                user=user,
                exam=exam,
                word=word,
                answer=selected_translation
            )
        if exam:
            word_exam = Word_Exam.objects.filter(exam=exam, word_id=word_id, done=False).first()
            if word_exam:
                word_exam.done = True
                word_exam.save()
            else:
                return redirect(reverse("folders_words:folders"))
        return self.get(request)
            
            