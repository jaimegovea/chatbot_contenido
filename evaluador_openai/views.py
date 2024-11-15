from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.core.files.storage import FileSystemStorage
from .models import (
    Apikeys,
    Rubrics,
    Ensayos,
    Videos,
    Syllabus,
    Questionnaire,
    Assignments,
    LabGuides,
    Presentations,
)
from .controllers import (
    read_docx,
    read_pdf,
    grade_essay,
    analyze_video,
    review_video,
    generate_syllabus,
    generate_questionnaire,
    generate_report,
    grade_assignment,
    read_doc,
    generate_lab_guide,
    generate_rubric,
    generate_pptx,
)
from datetime import date
from docxtpl import DocxTemplate
import os
import openai
import json
import zipfile

# Create your views here.


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Sesión iniciada")
        else:
            messages.error(request, "Credenciales incorrectas", extra_tags="danger")
        return redirect("rubrics")
    if request.user.is_authenticated:
        return redirect("rubrics")
    return render(request, "login.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        api_key = request.POST["api_key"]
        user = User.objects.create_user(username=username, password=password)
        user.save()
        login(request, user)
        new_api_key = Apikeys(user_id=request.user.id, api_key=api_key)
        new_api_key.save()
        messages.success(request, "Usuario registrado")
        return redirect("rubrics")
    if request.user.is_authenticated:
        return redirect("rubrics")
    return render(request, "register.html")


def logout_user(request):
    logout(request)
    messages.info(request, "Sesión terminada")
    return redirect("login_user")


@login_required(login_url="/login")
def rubrics(request):
    if request.method == "POST":
        name = request.POST["name"]
        content = request.POST["content"]
        new_rubric = Rubrics(name=name, content=content, user_id=request.user.id)
        new_rubric.save()
        messages.success(request, "Rubrica agregada")
        return redirect("rubrics")
    rubrics = Rubrics.objects.all().filter(user_id=request.user.id)
    return render(request, "rubrics.html", {"rubrics": rubrics})


@login_required(login_url="/login")
def new_rubric(request):
    return render(request, "new_rubric.html")


@login_required(login_url="/login")
def rubric_detail(request, rubric_id):
    rubric = Rubrics.objects.get(id=rubric_id)
    return render(request, "rubric_detail.html", {"rubric": rubric})


@login_required(login_url="/login")
def rubric_edit(request, rubric_id):
    rubric = Rubrics.objects.get(id=rubric_id)
    if request.method == "POST":
        name = request.POST["name"]
        content = request.POST["content"]
        rubric.name = name
        rubric.content = content
        rubric.save()
        messages.success(request, "Rúbrica editada")
        return redirect("rubrics")
    return render(request, "rubric_edit.html", {"rubric": rubric})


@login_required(login_url="/login")
def rubric_delete(request, rubric_id):
    if request.method == "POST":
        rubric = Rubrics.objects.get(id=rubric_id)
        rubric.delete()
        messages.success(request, "Rúbrica eliminada")
        return redirect("rubrics")


@login_required(login_url="/login")
def essays(request):
    if request.method == "POST":
        criteria_id = request.POST["criteria"]
        rubric = Rubrics.objects.get(id=criteria_id)
        api_key = Apikeys.objects.get(user_id=request.user.id)
        theme = request.POST["theme"]
        file = request.FILES["essay"]
        if file.name.endswith("docx"):
            content = read_docx(file)
        elif file.name.endswith("pdf"):
            content = read_pdf(file)
        try:
            analysis = grade_essay(
                criteria=rubric.content,
                theme=theme,
                ensayo=content,
                api_key=api_key.api_key,
            )
            new_essay = Ensayos(
                criteria_id=criteria_id,
                theme=theme,
                file_name=file.name,
                file_path=file,
                analysis=analysis,
                date=date.today(),
                user_id=request.user.id,
                criteria_name=rubric.name,
            )
            new_essay.save()
            messages.success(request, "Ensayo evaluado")
            return JsonResponse({"success": True})
        except openai.AuthenticationError:
            return JsonResponse({"success": False})
    essays = Ensayos.objects.all().filter(user_id=request.user.id)
    return render(request, "essays.html", {"essays": essays})


@login_required(login_url="/login")
def new_essay(request):
    rubrics = Rubrics.objects.all().filter(user_id=request.user.id)
    return render(request, "new_essay.html", {"rubrics": rubrics})


@login_required(login_url="/login")
def essay_detail(request, essay_id):
    essay = Ensayos.objects.get(id=essay_id)
    return render(request, "essay_detail.html", {"essay": essay})


@login_required(login_url="/login")
def essay_edit(request, essay_id):
    essay = Ensayos.objects.get(id=essay_id)
    if request.method == "POST":
        criteria_id = request.POST["criteria"]
        rubric = Rubrics.objects.get(id=criteria_id)
        api_key = Apikeys.objects.get(user_id=request.user.id)
        theme = request.POST["theme"]
        file = essay.file_path
        if file.name.endswith("docx"):
            content = read_docx(file.name)
        elif file.name.endswith("pdf"):
            content = read_pdf(file.name)
        analysis = grade_essay(
            criteria=rubric.content,
            theme=theme,
            ensayo=content,
            api_key=api_key.api_key,
        )
        essay.theme = theme
        essay.criteria = rubric
        essay.analysis = analysis
        essay.date = date.today()
        essay.save()
        messages.success(request, "Ensayo re-eveluado")
        return redirect("essays")
    rubrics = Rubrics.objects.all().filter(user_id=request.user.id)
    return render(request, "essay_edit.html", {"essay": essay, "rubrics": rubrics})


@login_required(login_url="/login")
def essay_delete(request, essay_id):
    if request.method == "POST":
        essay = Ensayos.objects.get(id=essay_id)
        essay.delete()
        messages.success(request, "Ensayo eliminado")
        return redirect("essays")


@login_required(login_url="/login")
def essay_report(request):
    if request.method == "POST":
        date = request.POST["date"]
        file_path = generate_report(
            table_name="evaluador_openai_ensayos",
            user_id=request.user.id,
            date=date,
            columns_to_drop=["id", "criteria_id", "date", "user_id", "file_path"],
        )
        response = FileResponse(open(file_path, "rb"))
        response["Content-Type"] = "application/ms-excel"
        response["Content-Disposition"] = "attachment; filename=report.xlsx"
        return response
    return render(request, "essay_report.html")


@login_required(login_url="/login")
def videos(request):
    if request.method == "POST":
        criteria_id = request.POST["criteria"]
        rubric = Rubrics.objects.get(id=criteria_id)
        api_key = Apikeys.objects.get(user_id=request.user.id)
        file = request.FILES["video"]
        FileSystemStorage(location="media/videos").save(file.name, file)
        temp_path = os.path.join("media", "videos", file.name)
        try:
            transcription, analysis = analyze_video(
                criteria=rubric.content,
                video_path=temp_path,
                file_name=file.name,
                api_key=api_key.api_key,
            )
            new_video = Videos(
                user_id=request.user.id,
                criteria_name=rubric.name,
                criteria_id=criteria_id,
                file_name=file.name,
                file_path=temp_path,
                transcription=transcription,
                analysis=analysis,
                date=date.today(),
            )
            new_video.save()
            messages.success(request, "Video analizado")
            return JsonResponse({"success": True})
        except openai.AuthenticationError:
            return JsonResponse({"success": False})
    videos = Videos.objects.all().filter(user_id=request.user.id)
    return render(request, "videos.html", {"videos": videos})


@login_required(login_url="/login")
def new_video(request):
    rubrics = Rubrics.objects.all().filter(user_id=request.user.id)
    return render(request, "new_video.html", {"rubrics": rubrics})


@login_required(login_url="/login")
def video_detail(request, video_id):
    video = Videos.objects.get(id=video_id)
    return render(request, "video_detail.html", {"video": video})


@login_required(login_url="/login")
def video_edit(request, video_id):
    video = Videos.objects.get(id=video_id)
    if request.method == "POST":
        criteria_id = request.POST["criteria"]
        rubric = Rubrics.objects.get(id=criteria_id)
        api_key = Apikeys.objects.get(user_id=request.user.id)
        analysis = review_video(
            criteria=rubric.content,
            transcription=video.transcription,
            api_key=api_key.api_key,
        )
        video.criteria_id = rubric.id
        video.criteria_name = rubric.name
        video.analysis = analysis
        video.date = date.today()
        video.save()
        messages.success(request, "Video re-calificado")
        return redirect("videos")
    rubrics = Rubrics.objects.all().filter(user_id=request.user.id)
    return render(request, "video_edit.html", {"video": video, "rubrics": rubrics})


@login_required(login_url="/login")
def video_delete(request, video_id):
    if request.method == "POST":
        video = Videos.objects.get(id=video_id)
        video.delete()
        messages.success(request, "Video eliminado")
        return redirect("videos")


@login_required(login_url="/login")
def video_report(request):
    if request.method == "POST":
        date = request.POST["date"]
        file_path = generate_report(
            table_name="evaluador_openai_videos",
            user_id=request.user.id,
            date=date,
            columns_to_drop=["id", "criteria_id", "date", "user_id", "file_path"],
        )
        response = FileResponse(open(file_path, "rb"))
        response["Content-Type"] = "application/ms-excel"
        response["Content-Disposition"] = "attachment; filename=report.xlsx"
        return response
    return render(request, "video_report.html")


@login_required(login_url="/login")
def syllabus(request):
    if request.method == "POST":
        api_key = Apikeys.objects.get(user_id=request.user.id)
        subject = request.POST["subject"]
        rda = request.POST["rda"]
        description = request.POST["description"]
        sessions = request.POST["sessions"]
        content = generate_syllabus(
            subject=subject,
            rda=rda,
            description=description,
            sessions=sessions,
            api_key=api_key.api_key,
        )
        new_syllabus = Syllabus(
            subject=subject,
            rda=rda,
            description=description,
            sessions=sessions,
            content=content,
            user_id=request.user.id,
            date=date.today(),
        )
        new_syllabus.save()
        messages.success(request, "Sílabo generado")
        return redirect("syllabus")
    syllabus = Syllabus.objects.all().filter(user_id=request.user.id)
    return render(request, "syllabus.html", {"syllabus": syllabus})


@login_required(login_url="/login")
def new_syllabus(request):
    return render(request, "new_syllabus.html")


@login_required(login_url="/login")
def syllabus_detail(request, syllabus_id):
    syllabus = Syllabus.objects.get(id=syllabus_id)
    syllabus_dict = json.loads(syllabus.content)
    if request.method == "POST":
        context = {
            "course_name": syllabus_dict["course"],
            "description": syllabus_dict["description"],
            "rdas": syllabus_dict["objectives"],
            "sessions": syllabus_dict["sessions"],
        }
        template_path = os.path.join("media", "reports", "syllabus_template.docx")
        new_report_path = os.path.join("media", "reports", "syllabus.docx")
        doc = DocxTemplate(template_path)
        doc.render(context)
        doc.save(new_report_path)
        response = FileResponse(open(new_report_path, "rb"))
        response["Content-Type"] = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response["Content-Disposition"] = "attachment; filename=syllabus.docx"
        return response
    return render(
        request,
        "syllabus_detail.html",
        {"syllabus": syllabus, "content": syllabus_dict},
    )


@login_required(login_url="/login")
def syllabus_edit(request, syllabus_id):
    syllabus = Syllabus.objects.get(id=syllabus_id)
    if request.method == "POST":
        api_key = Apikeys.objects.get(user_id=request.user.id)
        subject = request.POST["subject"]
        description = request.POST["description"]
        rda = request.POST["rda"]
        sessions = request.POST["sessions"]
        content = generate_syllabus(
            subject=subject,
            rda=rda,
            description=description,
            sessions=sessions,
            api_key=api_key.api_key,
        )
        syllabus.subject = subject
        syllabus.description = description
        syllabus.rda = rda
        syllabus.sessions = sessions
        syllabus.content = content
        syllabus.date = date.today()
        syllabus.save()
        messages.success(request, "Sílabo re-generado")
        return redirect("syllabus")
    return render(request, "syllabus_edit.html", {"syllabus": syllabus})


@login_required(login_url="/login")
def syllabus_delete(request, syllabus_id):
    syllabus = Syllabus.objects.get(id=syllabus_id)
    syllabus.delete()
    messages.success(request, "Sílabo eliminado")
    return redirect("syllabus")


@login_required(login_url="/login")
def syllabus_report(request):
    if request.method == "POST":
        date = request.POST["date"]
        file_path = generate_report(
            table_name="evaluador_openai_syllabus",
            user_id=request.user.id,
            date=date,
            columns_to_drop=["id", "date", "user_id"],
        )
        response = FileResponse(open(file_path, "rb"))
        response["Content-Type"] = "application/ms-excel"
        response["Content-Disposition"] = "attachment; filename=report.xlsx"
        return response
    return render(request, "syllabus_report.html")


@login_required(login_url="/login")
def new_lab_guide(request, syllabus_id):
    if request.method == "POST":
        syllabus = Syllabus.objects.get(id=syllabus_id)
        api_key = Apikeys.objects.get(user_id=request.user.id)
        lab_guides = generate_lab_guide(syllabus.content, api_key.api_key)
        new_lab_guide = LabGuides(
            user_id=request.user.id,
            syllabus=syllabus,
            content=lab_guides,
            date=date.today(),
        )
        new_lab_guide.save()
        lab_guide_dict = json.loads(lab_guides)
        lab_guide_list = []
        for i in range(len(lab_guide_dict["sessions"])):
            context = {
                "course": lab_guide_dict["course"],
                "workshop_name": lab_guide_dict["sessions"][i]["workshop_name"],
                "objectives": lab_guide_dict["sessions"][i]["objectives"],
                "rda": lab_guide_dict["sessions"][i]["rda"],
                "introduction": lab_guide_dict["sessions"][i]["introduction"],
                "materials": lab_guide_dict["sessions"][i]["materials"],
                "methodology": lab_guide_dict["sessions"][i]["methodology"],
                "references": lab_guide_dict["sessions"][i]["references"],
                "annexes": lab_guide_dict["sessions"][i]["annexes"],
            }
            template_path = os.path.join("media", "reports", "lab_template.docx")
            new_report_path = os.path.join("media", "reports", f"lab_guide_{i}.docx")
            doc = DocxTemplate(template_path)
            doc.render(context)
            doc.save(new_report_path)
            lab_guide_list.append(new_report_path)
        lab_guides_zip_path = os.path.join("media", "reports", "lab_guides.zip")
        with zipfile.ZipFile(lab_guides_zip_path, "w") as zip:
            for file in lab_guide_list:
                zip.write(file)
        response = FileResponse(open(lab_guides_zip_path, "rb"))
        response["Content-Type"] = (
            "application/zip"
        )
        response["Content-Disposition"] = "attachment; filename=lab_guides.zip"
        return response
    

@login_required(login_url="/login")
def new_rubric_dict(request, syllabus_id):
    if request.method == "POST":
        syllabus = Syllabus.objects.get(id=syllabus_id)
        api_key = Apikeys.objects.get(user_id=request.user.id)
        rubric = generate_rubric(syllabus.content, api_key.api_key)
        new_rubric = Rubrics(name=syllabus.subject, content=rubric, user_id=request.user.id)
        new_rubric.save()
        rubric_dict = json.loads(rubric)
        rubric_list = []
        for key in rubric_dict:
            context = {
                "content": rubric_dict[key]
            }
            template_path = os.path.join("media", "reports", "rubric_template.docx")
            new_report_path = os.path.join("media", "reports", f"{key}_rubric.docx")
            doc = DocxTemplate(template_path)
            doc.render(context)
            doc.save(new_report_path)
            rubric_list.append(new_report_path)
        lab_guides_zip_path = os.path.join("media", "reports", "lab_guides.zip")
        with zipfile.ZipFile(lab_guides_zip_path, "w") as zip:
            for file in rubric_list:
                zip.write(file)
        response = FileResponse(open(lab_guides_zip_path, "rb"))
        response["Content-Type"] = (
            "application/zip"
        )
        response["Content-Disposition"] = "attachment; filename=rubrics.zip"
        return response
    

@login_required(login_url="/login")
def new_pptx_dict(request, syllabus_id):
    if request.method == "POST":
        syllabus = Syllabus.objects.get(id=syllabus_id)
        api_key = Apikeys.objects.get(user_id=request.user.id)
        pptx = generate_pptx(syllabus.content, api_key.api_key)
        new_pptx = Presentations(user_id=request.user.id,
            syllabus=syllabus,
            content=pptx,
            date=date.today(),)
        new_pptx.save()
        pptx_dict = json.loads(pptx)
        pptx_list = []
        for p in pptx_dict["presentations"]:
            context = {
                "content": p
            }
            template_path = os.path.join("media", "reports", "presentation_template.docx")
            new_report_path = os.path.join("media", "reports", f"{p['title']}_presentation_content.docx")
            doc = DocxTemplate(template_path)
            doc.render(context)
            doc.save(new_report_path)
            pptx_list.append(new_report_path)
        lab_guides_zip_path = os.path.join("media", "reports", "lab_guides.zip")
        with zipfile.ZipFile(lab_guides_zip_path, "w") as zip:
            for file in pptx_list:
                zip.write(file)
        response = FileResponse(open(lab_guides_zip_path, "rb"))
        response["Content-Type"] = (
            "application/zip"
        )
        response["Content-Disposition"] = "attachment; filename=presentation_content.zip"
        return response


@login_required(login_url="/login")
def questionnaire(request):
    if request.method == "POST":
        api_key = Apikeys.objects.get(user_id=request.user.id)
        subject = request.POST["subject"]
        questions = request.POST["questions"]
        topics = request.POST["topics"]
        content = generate_questionnaire(
            subject=subject, questions=questions, topics=topics, api_key=api_key.api_key
        )
        new_questionnaire = Questionnaire(
            subject=subject,
            questions=questions,
            topics=topics,
            content=content,
            user_id=request.user.id,
            date=date.today(),
        )
        new_questionnaire.save()
        messages.success(request, "Cuestionario generado")
        return redirect("questionnaires")
    questionnaires = Questionnaire.objects.all().filter(user_id=request.user.id)
    return render(request, "questionnaires.html", {"questionnaires": questionnaires})


@login_required(login_url="/login")
def new_questionnaire(request):
    return render(request, "new_questionnaire.html")


@login_required(login_url="/login")
def questionnaire_detail(request, questionnaire_id):
    questionnaire = Questionnaire.objects.get(id=questionnaire_id)
    return render(
        request, "questionnaire_detail.html", {"questionnaire": questionnaire}
    )


@login_required(login_url="/login")
def questionnaire_edit(request, questionnaire_id):
    questionnaire = Questionnaire.objects.get(id=questionnaire_id)
    if request.method == "POST":
        api_key = Apikeys.objects.get(user_id=request.user.id)
        subject = request.POST["subject"]
        questions = request.POST["questions"]
        topics = request.POST["topics"]
        content = generate_questionnaire(
            subject=subject, questions=questions, topics=topics, api_key=api_key.api_key
        )
        questionnaire.subject = subject
        questionnaire.topics = topics
        questionnaire.content = content
        questionnaire.questions = questions
        questionnaire.date = date.today()
        questionnaire.save()
        messages.success(request, "Cuestionario re-generado")
        return redirect("questionnaires")
    return render(request, "questionnaire_edit.html", {"questionnaire": questionnaire})


@login_required(login_url="/login")
def questionnaire_delete(request, questionnaire_id):
    if request.method == "POST":
        questionnaire = Questionnaire.objects.get(id=questionnaire_id)
        questionnaire.delete()
        messages.success(request, "Cuestionario eliminado")
        return redirect("questionnaires")


@login_required(login_url="/login")
def questionnaire_report(request):
    if request.method == "POST":
        date = request.POST["date"]
        file_path = generate_report(
            table_name="evaluador_openai_questionnaire",
            user_id=request.user.id,
            date=date,
            columns_to_drop=["id", "date", "user_id"],
        )
        response = FileResponse(open(file_path, "rb"))
        response["Content-Type"] = "application/ms-excel"
        response["Content-Disposition"] = "attachment; filename=report.xlsx"
        return response
    return render(request, "questionnaire_report.html")


@login_required(login_url="/login")
def assignments(request):
    assignments = Assignments.objects.all().filter(user_id=request.user.id)
    if request.method == "POST":
        criteria_id = request.POST["criteria"]
        rubric = Rubrics.objects.get(id=criteria_id)
        api_key = Apikeys.objects.get(user_id=request.user.id)
        description = request.POST["description"]
        file = request.FILES["essay"]
        if file.name.lower().endswith("docx"):
            content = read_docx(file)
        elif file.name.lower().endswith("pdf"):
            content = read_pdf(file)
        elif file.name.lower().endswith("doc") or file.name.endswith("DOC"):
            content = read_docx(file)
        try:
            analysis = grade_assignment(
                criteria=rubric.content,
                description=description,
                assignment=content,
                api_key=api_key.api_key,
            )
            new_assignment = Assignments(
                criteria_id=criteria_id,
                description=description,
                file_name=file.name,
                file_path=file,
                analysis=analysis,
                date=date.today(),
                user_id=request.user.id,
                criteria_name=rubric.name,
            )
            new_assignment.save()
            messages.success(request, "Tarea evaluada")
            return JsonResponse({"success": True})
        except openai.AuthenticationError:
            return JsonResponse({"success": False})
    return render(request, "assignments.html", {"assignments": assignments})


@login_required(login_url="/login")
def new_assignment(request):
    rubrics = Rubrics.objects.all().filter(user_id=request.user.id)
    return render(request, "new_assignment.html", {"rubrics": rubrics})


@login_required(login_url="/login")
def assignment_detail(request, assignment_id):
    assignment = Assignments.objects.get(id=assignment_id)
    return render(request, "assignment_detail.html", {"assignment": assignment})


@login_required(login_url="/login")
def assignment_edit(request, assignment_id):
    assignment = Assignments.objects.get(id=assignment_id)
    if request.method == "POST":
        criteria_id = request.POST["criteria"]
        description = request.POST["description"]
        rubric = Rubrics.objects.get(id=criteria_id)
        api_key = Apikeys.objects.get(user_id=request.user.id)
        file = assignment.file_path
        if file.name.lower().endswith("pdf"):
            content = read_pdf(file)
        elif file.name.namelower().endswith("docx") or file.name.lower().endswith(
            "doc"
        ):
            content = read_docx(file)
        analysis = grade_assignment(
            criteria=rubric.content,
            description=description,
            assignment=content,
            api_key=api_key.api_key,
        )
        assignment.criteria = rubric
        assignment.criteria_name = rubric.name
        assignment.description = description
        assignment.analysis = analysis
        assignment.date = date.today()
        assignment.save()
        messages.success(request, "Tarea recalificada")
        return redirect("assignments")
    rubrics = Rubrics.objects.all().filter(user_id=request.user.id)
    return render(
        request, "assignment_edit.html", {"assignment": assignment, "rubrics": rubrics}
    )


@login_required(login_url="/login")
def assignment_delete(request, assignment_id):
    if request.method == "POST":
        assignment = Assignments.objects.get(id=assignment_id)
        assignment.delete()
        messages.success(request, "Tarea eliminada")
        return redirect("assignments")


@login_required(login_url="/login")
def assignment_report(request):
    if request.method == "POST":
        date = request.POST["date"]
        file_path = generate_report(
            table_name="evaluador_openai_assignments",
            user_id=request.user.id,
            date=date,
            columns_to_drop=["id", "criteria_id", "date", "user_id", "file_path"],
        )
        response = FileResponse(open(file_path, "rb"))
        response["Content-Type"] = "application/ms-excel"
        response["Content-Disposition"] = "attachment; filename=report.xlsx"
        return response
    return render(request, "assignment_report.html")


@login_required(login_url="/login")
def update_api_key(request):
    if request.method == "POST":
        new_api_key = request.POST["api_key"]
        api_key = Apikeys.objects.get(user_id=request.user.id)
        api_key.api_key = new_api_key
        api_key.save()
        messages.success(request, "Llave de OpenAI actualizada")
        return JsonResponse({"success": True})
