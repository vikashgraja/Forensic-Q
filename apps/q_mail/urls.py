from django.urls import path

from . import views

app_name = "q_mail"

urlpatterns = [
    path("", views.investigation_list_view, name="list"),
    path("upload/initiate/", views.initiate_upload_view, name="upload_initiate"),
    path("upload/chunk/", views.chunk_upload_view, name="upload_chunk"),
    path("investigation/<uuid:mailbox_id>/", views.investigation_detail_view, name="detail"),
    path(
        "investigation/<uuid:mailbox_id>/process/",
        views.trigger_processing_view,
        name="trigger_process",
    ),
    path("investigation/<uuid:mailbox_id>/progress/", views.progress_api_view, name="progress_api"),
    path("investigation/<uuid:mailbox_id>/messages/", views.messages_api_view, name="messages_api"),
    path("email/<uuid:email_id>/", views.email_detail_api_view, name="email_detail"),
    path(
        "attachment/<uuid:attachment_id>/download/",
        views.download_attachment_view,
        name="download_attachment",
    ),
]
