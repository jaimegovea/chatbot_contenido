# Generated by Django 5.0.6 on 2024-07-05 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluador_openai', '0010_alter_videos_file_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaire',
            name='topics',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
    ]