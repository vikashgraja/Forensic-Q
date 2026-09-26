from django.contrib import admin

from .models import EmailAttachment, EmailMessage, EmailParticipant, MailboxInvestigation


class EmailAttachmentInline(admin.TabularInline):
    model = EmailAttachment
    extra = 0
    readonly_fields = ("filename", "file_size_bytes", "mime_type", "sha256_hash", "storage_path")


@admin.register(MailboxInvestigation)
class MailboxInvestigationAdmin(admin.ModelAdmin):
    list_display = (
        "audit_ref",
        "auditee_name",
        "auditee_email",
        "auditee_department",
        "status",
        "processed_messages_count",
        "created_at",
    )
    list_filter = ("status", "auditee_department", "created_at")
    search_fields = ("audit_ref", "audit_name", "auditee_name", "auditee_email", "pst_file_name")
    readonly_fields = (
        "file_sha256",
        "file_size_bytes",
        "processed_messages_count",
        "attachment_count",
        "created_at",
        "updated_at",
    )


@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = (
        "sender_email",
        "subject",
        "sent_date",
        "folder_path",
        "has_attachments",
        "attachment_count",
        "risk_score",
    )
    list_filter = ("has_attachments", "risk_level", "sent_date", "mailbox")
    search_fields = ("subject", "sender_name", "sender_email", "body_plain", "message_id")
    readonly_fields = ("message_id", "sent_date", "delivery_date", "created_at", "updated_at")
    inlines = [EmailAttachmentInline]


@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    list_display = ("filename", "email", "file_size_bytes", "mime_type", "sha256_hash")
    search_fields = ("filename", "sha256_hash")
    list_filter = ("mime_type", "is_suspicious")


@admin.register(EmailParticipant)
class EmailParticipantAdmin(admin.ModelAdmin):
    list_display = ("email_address", "display_name", "mailbox", "sent_count", "is_external_domain")
    search_fields = ("email_address", "display_name")
    list_filter = ("is_external_domain", "mailbox")
