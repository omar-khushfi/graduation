import random
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from rapidfuzz import fuzz
from .models import *
from accounts.models import *
from folders_words.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

class CreateExamView(LoginRequiredMixin,View):
    login_url = 'account/login/'  

    def get(self, request):
        languages = Language.objects.filter(user=request.user)
        return render(request, "create_exam.html", {"languages": languages})
    
    def post(self, request):
        user = request.user
        language_id = request.POST.get("lang")
        language = Language.objects.get(id=language_id, user=user)
        exam = self.get_or_create_exam(user, language)
        return redirect(reverse('exam:exam', kwargs={'lan': language.id}))
    
    def get_or_create_exam(self, user, language):
        now = datetime.now()
        exam = Exam.objects.filter(user=user, language=language, end__gt=now, finish=False).first()
        if not exam:
            exam = Exam.objects.create(
                user=user,
                language=language,
                end=datetime.now() + timedelta(seconds=50),
            )
            words = Word.objects.filter(study=False).order_by('?')[:15]
            for word in words:
                Word_Exam.objects.create(user=user, word=word, exam=exam)
        return exam


class ExamView(LoginRequiredMixin,View):
    login_url = 'account/login/'  

    def get(self, request, lan):
        user = request.user
        language = Language.objects.get(id=lan)
        now = datetime.now()
        exam = Exam.objects.filter(user=user, language=language, finish=False).first()
        word_exam = Word_Exam.objects.filter(exam=exam, done=False).first()
        print(word_exam)
        if not word_exam:
            context = self.build_result_context(user, exam)
            return render(request, "result.html", context)
        
        context = self.get_exam_context(user, exam, language, word_exam)
        return render(request, "exam.html", context)
    
    def post(self, request, lan):
        user = request.user
        language = Language.objects.get(id=lan)
        exam_id = request.POST.get("exam")
        exam = Exam.objects.get(id=exam_id)
        word_id = request.POST.get("current_word")
        word = Word.objects.get(id=word_id)
        answer_input = request.POST.get("ans")
        answer_type = request.POST.get("type")
        text_to_voice = request.POST.get("text_to_voice")
        true_translation_input = request.POST.get("true-translation")
        
        if not Answer.objects.filter(user=user, exam=exam, word=word).exists():
            processed_answer = self.process_answer(
                answer_type, true_translation_input, text_to_voice, answer_input, word
            )
            is_true = processed_answer.startswith("true-")
            if is_true:
                processed_answer = processed_answer[5:]
            Answer.objects.create(
                user=user,
                exam=exam,
                word=word,
                answer=processed_answer,
                is_true=is_true,
            )
        
        word_exam = Word_Exam.objects.filter(exam=exam, word_id=word_id, done=False).first()
        if word_exam:
            word_exam.done = True
            word_exam.save()
        
        if Word_Exam.objects.filter(exam=exam, done=False).count() < 1:
            exam.finish = True
            exam.save()
            context = self.build_result_context(user, exam)
            return render(request, "result.html", context)
        
        return self.get(request, lan)
    
    def process_answer(self, answer_type, true_translation, text_to_voice, current_answer, word):
       
        if answer_type == "voice" and text_to_voice:
            true_translation_clean = true_translation.lower().strip()
            text_to_voice_clean = text_to_voice.lower().strip()
            
            similarity_score = fuzz.WRatio(true_translation_clean, text_to_voice_clean)
            
            if similarity_score >= 80:
                return "true-" + text_to_voice_clean
            return text_to_voice_clean
        
        return current_answer

    
    def build_result_context(self, user, exam):
        """
        بناء سياق النتيجة عن طريق جلب الإجابات وترجمتها الصحيحة.
        """
        answers_result = {}
        answers = Answer.objects.filter(user=user, exam=exam)
        for answer in answers:
            true_translate = Translate.objects.get(word=answer.word, user=user, language=exam.language)
            answers_result[answer] = true_translate
        return {"answers_result": answers_result}
    
    def get_exam_context(self, user, exam, language, word_exam):
        """
        بناء سياق السؤال الحالي مع جلب الترجمات الصحيحة والخاطئة.
        """
        true_translate = Translate.objects.get(user=user, word=word_exam.word, language=language)
        false_translations = list(
            Translate.objects.filter(user=user, language=language).exclude(word=word_exam.word)[:2]
        )
        native_translate = Translate.objects.get(user=user, language__is_native=True, word=word_exam.word)
        words_with_translate = {
            'true': true_translate,
            'false1': false_translations[0] if len(false_translations) > 0 else None,
            'false2': false_translations[1] if len(false_translations) > 1 else None,
        }
        return {
            'type': random.choice(['choose', 'voice', 'hear']),
            'lang': language.id,
            'exam': exam,
            'words_with_translate': words_with_translate,
            'current_word': word_exam.word,
            'native_translate': native_translate,
        }
