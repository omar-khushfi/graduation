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
        ('af', 'Afrikaans'),
        ('am', 'Amharic'),
        ('ar', 'Arabic'),
        ('bg', 'Bulgarian'),
        ('bn', 'Bengali'),
        ('bs', 'Bosnian'),
        ('ca', 'Catalan'),
        ('cs', 'Czech'),
        ('cy', 'Welsh'),
        ('da', 'Danish'),
        ('de', 'German'),
        ('el', 'Greek'),
        ('en', 'English'),
        ('es', 'Spanish'),
        ('et', 'Estonian'),
        ('eu', 'Basque'),
        ('fi', 'Finnish'),
        ('fr', 'French'),
        ('fr-CA', 'French (Canada)'),
        ('gl', 'Galician'),
        ('gu', 'Gujarati'),
        ('ha', 'Hausa'),
        ('hi', 'Hindi'),
        ('hr', 'Croatian'),
        ('hu', 'Hungarian'),
        ('id', 'Indonesian'),
        ('is', 'Icelandic'),
        ('it', 'Italian'),
        ('iw', 'Hebrew'),
        ('ja', 'Japanese'),
        ('jw', 'Javanese'),
        ('km', 'Khmer'),
        ('kn', 'Kannada'),
        ('ko', 'Korean'),
        ('la', 'Latin'),
        ('lt', 'Lithuanian'),
        ('lv', 'Latvian'),
        ('ml', 'Malayalam'),
        ('mr', 'Marathi'),
        ('ms', 'Malay'),
        ('my', 'Myanmar (Burmese)'),
        ('ne', 'Nepali'),
        ('nl', 'Dutch'),
        ('no', 'Norwegian'),
        ('pa', 'Punjabi (Gurmukhi)'),
        ('pl', 'Polish'),
        ('pt', 'Portuguese (Brazil)'),
        ('pt-PT', 'Portuguese (Portugal)'),
        ('ro', 'Romanian'),
        ('ru', 'Russian'),
        ('si', 'Sinhala'),
        ('sk', 'Slovak'),
        ('sq', 'Albanian'),
        ('sr', 'Serbian'),
        ('su', 'Sundanese'),
        ('sv', 'Swedish'),
        ('sw', 'Swahili'),
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
        ('th', 'Thai'),
        ('tl', 'Filipino'),
        ('tr', 'Turkish'),
        ('uk', 'Ukrainian'),
        ('ur', 'Urdu'),
        ('vi', 'Vietnamese'),
        ('yue', 'Cantonese'),
        ('zh-CN', 'Chinese (Simplified)'),
        ('zh-TW', 'Chinese (Traditional)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
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