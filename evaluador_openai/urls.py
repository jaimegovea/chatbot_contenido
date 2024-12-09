from django.urls import path

from . import views

urlpatterns = [
    path("", views.login_user, name="login_user"),
    path("login/", views.login_user, name="login_user"),
    path("register", views.register, name="register"),
    path("logout", views.logout_user, name="logout_user"),
    path("rubrics", views.rubrics, name="rubrics"),
    path("rubrics/new", views.new_rubric, name="new_rubric"),
    path("rubrics/<int:rubric_id>", views.rubric_detail, name='rubric_detail'),
    path("rubrics/edit/<int:rubric_id>", views.rubric_edit, name="rubric_edit"),
    path("rubrics/delete/<int:rubric_id>", views.rubric_delete, name="rubric_delete"),
    path("essays", views.essays, name="essays"),
    path("essays/new", views.new_essay, name="new_essay"),
    path("essays/<int:essay_id>", views.essay_detail, name="essay_detail"),
    path("essays/edit/<int:essay_id>", views.essay_edit, name="essay_edit"),
    path("essays/delete/<int:essay_id>", views.essay_delete, name="essay_delete"),
    path("essays/report", views.essay_report, name="essay_report"),
    path("videos", views.videos, name="videos"),
    path("videos/new", views.new_video, name="new_video"),
    path("videos/<int:video_id>", views.video_detail, name="video_detail"),
    path("videos/edit/<int:video_id>", views.video_edit, name="video_edit"),
    path("videos/delete/<int:video_id>", views.video_delete, name="video_delete"),
    path("videos/report", views.video_report, name="video_report"),
    path("syllabus", views.syllabus, name="syllabus"),
    path("syllabus/new", views.new_syllabus, name="new_syllabus"),
    path("syllabus/detail/<int:syllabus_id>", views.syllabus_detail, name="syllabus_detail"),
    path("syllabus/edit/<int:syllabus_id>", views.syllabus_edit, name="syllabus_edit"),
    path("syllabus/delete/<int:syllabus_id>", views.syllabus_delete, name="syllabus_delete"),
    path("syllabus/report", views.syllabus_report, name="syllabus_report"),
    path("questionnaires", views.questionnaire, name="questionnaires"),
    path("questionnaires/new", views.new_questionnaire, name="new_questionnaire"),
    path("questionnaires/detail/<int:questionnaire_id>", views.questionnaire_detail, name="questionnaire_detail"),
    path("questionnaires/edit/<int:questionnaire_id>", views.questionnaire_edit, name="questionnaire_edit"),
    path("questionnaires/delete/<int:questionnaire_id>", views.questionnaire_delete, name="questionnaire_delete"),
    path("questionnaires/report", views.questionnaire_report, name="questionnaire_report"),
    path("update_api_key", views.update_api_key, name="update_api_key"),
    path("assignments", views.assignments, name="assignments"),
    path("assignments/new", views.new_assignment, name="new_assignment"),
    path("assignments/<int:assignment_id>", views.assignment_detail, name="assignment_detail"),
    path("assignments/edit/<int:assignment_id>", views.assignment_edit, name="assignment_edit"),
    path("assignments/delete/<int:assignment_id>", views.assignment_delete, name="assignment_delete"),
    path("assignments/report", views.assignment_report, name="assignment_report"),
    path("lab_guides/new/<int:syllabus_id>", views.new_lab_guide, name="new_lab_guide"),
    path("rubric_dict/new/<int:syllabus_id>", views.new_rubric_dict, name="new_rubric_dict"),
    path("pptx_dict/new/<int:syllabus_id>", views.new_pptx_dict, name="new_pptx_dict"),
    path("syllabusapi", views.syllabusapi, name="syllabusapi"),
    path("syllabusdocapi/<int:syllabus_id>", views.syllabusdocapi, name="syllabusdocapi"),
    path("labguideapi/<int:syllabus_id>", views.new_lab_guide_api, name="new_lab_guide_api"),
    path("rubricdicapi/<int:syllabus_id>", views.new_rubric_dict_api, name="new_rubric_dict_api")
]