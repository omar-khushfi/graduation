import datetime
from django.shortcuts import render
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
        # تحقق من وجود اختبار قيد التنفيذ للمستخدم
        now = datetime.now()
        exam = Exam.objects.filter(user=user, language=lang, end__gt=now, finish=False).first()

        if not exam:  # إذا لم يكن هناك اختبار جاري، أنشئ اختبار جديد
            exam = Exam.objects.create(
                user=user,
                language=lang,
                end=datetime.now() + timedelta(seconds=15),
            )
            words = Word.objects.filter(study=False).order_by('?')[:15]
            for word in words:
                Word_Exam.objects.create(user=user, word=word, exam=exam)
        
        # الحصول على الكلمة الحالية بناءً على التقدم في الاختبار
        word_exam = Word_Exam.objects.filter(exam=exam, done=False).first()

        if not word_exam:  # إذا تم الانتهاء من الاختبار
            exam.finish = True
            exam.save()
            return render(request, "exam_result.html", {"exam": exam})
        
        # استخراج الترجمة الصحيحة والخاطئة
        true_translate = Translate.objects.get(user=user, word=word_exam.word, language=lang)
        false_translations = list(Translate.objects.filter(user=user, language=lang).exclude(word=word_exam.word)[:2])
        native_translate=Translate.objects.get(user=user,language__Is_Native=True,word=word_exam.word)
        # تجهيز البيانات لتمريرها إلى القالب
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
        # الحصول على الاختبار الحالي للمستخدم
        lang = Language.objects.get(id=lang)
        exam = Exam.objects.get(id=exam_id)

        if exam:
            word_exam = Word_Exam.objects.filter(exam=exam, word_id=word_id, done=False).first()

            if word_exam:
                word_exam.done = True
                word_exam.save()

        # إعادة تحميل الصفحة مع التقدم إلى الكلمة التالية
        return self.get(request)
            
            