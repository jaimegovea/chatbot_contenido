# Generated by Django 5.0.6 on 2024-07-05 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluador_openai', '0008_rename_file_ensayos_file_path_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='videos',
            old_name='user_id',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='videos',
            name='date',
            field=models.CharField(max_length=20),
        ),
    ]