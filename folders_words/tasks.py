# tasks.py
from celery import shared_task
import requests
import os
import re
from django.conf import settings
from gtts import gTTS
from .models import Word, Language, Translate

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

@shared_task
def process_translation_and_voice(user_id, word_id, language_id, main_lang_type):
    try:
        word_obj = Word.objects.get(id=word_id)
        language = Language.objects.get(id=language_id)
        
        if language.type != main_lang_type:
            translated = translate_text_mymemory(word_obj.content, main_lang_type, language.type)
        else:
            translated = word_obj.content

        voice_path = generate_pronunciation(translated, language, user_id)
        
        Translate.objects.create(
            user_id=user_id,
            language=language,
            word=word_obj,
            translation=translated,
            voice=voice_path
        )
    except Exception as e:
        # يمكنك تسجيل الخطأ أو التعامل معه بالشكل المناسب
        print(f"Error in process_translation_and_voice: {e}")
