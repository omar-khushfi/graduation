from django.db import models
from accounts.models import *
# Create your models here.



class Folder(models.Model):
    name=models.CharField(max_length=30)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    
    
    
class Word(models.Model):
    content=models.CharField(max_length=30)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    folder=models.ForeignKey(Folder,on_delete=models.CASCADE)
    study=models.BooleanField(default=False)
    def __str__(self):
        return self.user.username+" "+self.content
    

    
class Language(models.Model):
    LANGUAGE_CHOICES = [
        ('ar', 'العربية'),
        ('en', 'الإنجليزية'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    is_native = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'code')

    def __str__(self):
        return f"{self.user.username} - {self.get_code_display()}"
    
class Translate(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name="translations")
    language = models.ForeignKey(Language,on_delete=models.CASCADE)  
    translation = models.CharField(max_length=255)  
    voice=models.FileField(upload_to="voices/")
    def __str__(self):
        return self.user.username+"__"+self.translation