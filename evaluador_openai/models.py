from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Apikeys(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=100)


class Rubrics(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    content = models.TextField()


class Ensayos(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    criteria_name = models.CharField(max_length=1000)
    criteria = models.ForeignKey(Rubrics, on_delete=models.CASCADE)
    theme = models.CharField(max_length=200)
    file_name = models.CharField(max_length=500)
    file_path = models.FileField(upload_to="media/essays")
    analysis = models.CharField(max_length=10000)
    date = models.CharField(max_length=15)


class Questionnaire(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    topics = models.TextField()
    questions = models.IntegerField()
    content = models.TextField()
    date = models.CharField(max_length=40)


class Syllabus(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    rda = models.TextField()
    description = models.TextField()
    sessions = models.IntegerField()
    content = models.TextField()
    date = models.CharField(max_length=20)


class Videos(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    criteria_name = models.CharField(max_length=50)
    criteria = models.ForeignKey(Rubrics, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=100)
    file_path = models.CharField(max_length=200)
    transcription = models.CharField(max_length=7500)
    analysis = models.CharField(max_length=7500)
    date = models.CharField(max_length=20)


class Assignments(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    criteria_name = models.CharField(max_length=50)
    criteria = models.ForeignKey(Rubrics, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=100)
    file_path = models.FileField(upload_to="media/essays")
    description = models.TextField()
    analysis = models.TextField()
    date = models.CharField(max_length=20)


class LabGuides(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.CharField(max_length=20)


class Presentations(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.CharField(max_length=20)