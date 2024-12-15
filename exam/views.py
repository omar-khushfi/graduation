import datetime
import random
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
            answers_result={}
            answers=Answer.objects.filter(user=user,exam=exam)
            for answer in answers:
                true_translate=Translate.objects.get(word=answer.word,user=user,language=exam.language)
                answers_result[answer]=true_translate

            context={
                'answers_result':answers_result,
            }
            return render(request,"result.html",context)
        true_translate = Translate.objects.get(user=user, word=word_exam.word, language=lang)
        false_translations = list(Translate.objects.filter(user=user, language=lang).exclude(word=word_exam.word)[:2])
        native_translate=Translate.objects.get(user=user,language__Is_Native=True,word=word_exam.word)
       
        words_with_translate = {
            'true': true_translate,
            'false1': false_translations[0] if len(false_translations) > 0 else None,
            'false2': false_translations[1] if len(false_translations) > 1 else None,
           
        }
        context = {
            'type': random.choice(['choose','voice']),
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
        type=data.get("type")
        text_to_voice=data.get("text_to_voice")
        word=Word.objects.get(id=word_id)
        true_translation=data.get("true-translation")
        lang = Language.objects.get(id=lang)
        exam = Exam.objects.get(id=exam_id)
       
        if not Answer.objects.filter( user=user, exam=exam,word=word).exists():
            if type == "voice":
                word_content=word.content
                if true_translation.lower() in text_to_voice.lower():
                    selected_translation="true-"+text_to_voice 
                else:
                    selected_translation=text_to_voice
               
            if selected_translation.startswith("true"):
                Answer.objects.create(
                    user=user,
                    exam=exam,
                    word=word,
                    answer=selected_translation[5:],
                    is_true=True
                )
            else:
                    Answer.objects.create(
                        user=user,
                        exam=exam,
                        word=word,
                        answer=selected_translation
                    )
     
        word_exam = Word_Exam.objects.filter(exam=exam, word_id=word_id, done=False).first()
        if word_exam:
            word_exam.done = True
            word_exam.save()
        print(Word_Exam.objects.filter(exam=exam,done=False).count())
        if  Word_Exam.objects.filter(exam=exam,done=False).count() < 1:
            exam.finish=True
            exam.save()
            answers_result={}
            answers=Answer.objects.filter(user=user,exam=exam)
            for answer in answers:
                true_translate=Translate.objects.get(word=answer.word,user=user,language=exam.language)
                answers_result[answer]=true_translate

            context={
            'answers_result':answers_result,
            }
            return render(request,"result.html",context)
        return self.get(request)
            
            