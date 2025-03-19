from django.db import models
from accounts.models import *
from folders_words.models import *
# Create your models here.



class Exam(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    start=models.DateTimeField(auto_now=True)
    end=models.DateTimeField()
    language = models.ForeignKey(Language,on_delete=models.CASCADE)  
    finish=models.BooleanField(default=False)
    


class Word_Exam(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    word=models.ForeignKey(Word,on_delete=models.CASCADE)
    exam=models.ForeignKey(Exam,on_delete=models.CASCADE)
    done=models.BooleanField(default=False)
    
    
    
class Answer(models.Model):
   user=models.ForeignKey(User,on_delete=models.CASCADE)
   word=models.ForeignKey(Word,on_delete=models.CASCADE)
   exam=models.ForeignKey(Exam,on_delete=models.CASCADE)
   answer=models.CharField(max_length=100)
   is_true=models.BooleanField(default=False)
   created_at=models.DateTimeField(auto_now=True)