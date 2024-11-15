# Generated by Django 5.0.6 on 2024-07-02 20:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluador_openai', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='apikeys',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='questionnaire',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='rubrics',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='syllabus',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RemoveField(
            model_name='ensayos',
            name='criteria_id',
        ),
        migrations.RemoveField(
            model_name='videos',
            name='criteria_id',
        ),
        migrations.AddField(
            model_name='ensayos',
            name='criteria_name',
            field=models.CharField(default='NA', max_length=1000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='videos',
            name='criteria_name',
            field=models.CharField(default='NA', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ensayos',
            name='criteria',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluador_openai.rubrics'),
        ),
        migrations.AlterField(
            model_name='videos',
            name='criteria',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluador_openai.rubrics'),
        ),
    ]