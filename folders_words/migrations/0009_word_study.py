# Generated by Django 5.1.2 on 2024-11-10 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('folders_words', '0008_translate_voice'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='study',
            field=models.BooleanField(default=False),
        ),
    ]