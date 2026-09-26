from django.db import models

from core.models import ForensicBaseModel


class MailboxInvestigation(ForensicBaseModel):
    """
    Represents an audit investigation case and its ingested PST file.
    """

    class IngestionStatus(models.TextChoices):
        PENDING = "PENDING", "Pending Ingestion"
        UPLOADING = "UPLOADING", "Uploading PST File"
        PROCESSING = "PROCESSING", "Extracting & Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    # Audit & Auditee Details
    audit_ref = models.CharField(
        max_length=64, db_index=True, help_text="Audit Reference / Case Number"
    )
    audit_name = models.CharField(max_length=255, help_text="Investigation / Audit Title")
    auditee_name = models.CharField(max_length=255, help_text="Target Auditee / Custodian Name")
    auditee_email = models.EmailField(max_length=255, help_text="Auditee Primary Corporate Email")
    auditee_department = models.CharField(
        max_length=128, blank=True, default="", help_text="Department / Business Unit"
    )
    auditee_designation = models.CharField(
        max_length=128, blank=True, default="", help_text="Auditee Official Title"
    )

    # PST Evidence Artifact Details
    pst_file_name = models.CharField(max_length=255)
    pst_file_path = models.CharField(max_length=512, blank=True, default="")
    file_size_bytes = models.BigIntegerField(default=0)
    file_sha256 = models.CharField(
        max_length=64, blank=True, default="", help_text="Chain of Custody Hash"
    )

    # Ingestion & Asynchronous Task State
    status = models.CharField(
        max_length=32,
        choices=IngestionStatus.choices,
        default=IngestionStatus.PENDING,
        db_index=True,
    )
    progress_percent = models.FloatField(default=0.0)
    current_folder = models.CharField(max_length=255, blank=True, default="")
    total_messages_estimated = models.IntegerField(default=0)
    processed_messages_count = models.IntegerField(default=0)
    attachment_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, default="")
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Mailbox Investigation"
        verbose_name_plural = "Mailbox Investigations"

    def __str__(self) -> str:
        return f"[{self.audit_ref}] {self.auditee_name} ({self.auditee_email})"

    @property
    def formatted_size(self) -> str:
        size = self.file_size_bytes
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"


class EmailMessage(ForensicBaseModel):
    """
    Individual email message extracted from a PST mailbox.
    """

    mailbox = models.ForeignKey(
        MailboxInvestigation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    message_id = models.CharField(max_length=255, db_index=True, blank=True, default="")
    subject = models.TextField(blank=True, default="(No Subject)")
    sender_name = models.CharField(max_length=255, blank=True, default="")
    sender_email = models.CharField(max_length=255, db_index=True, blank=True, default="")
    recipients_to = models.JSONField(default=list, help_text="List of To recipients")
    recipients_cc = models.JSONField(default=list, help_text="List of Cc recipients")
    recipients_bcc = models.JSONField(default=list, help_text="List of Bcc recipients")
    sent_date = models.DateTimeField(null=True, blank=True, db_index=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    folder_path = models.CharField(max_length=512, blank=True, default="", db_index=True)

    # Body Content
    body_plain = models.TextField(blank=True, default="")
    body_html = models.TextField(blank=True, default="")

    # Forensic Flags & Metrics
    importance = models.IntegerField(default=1, help_text="0: Low, 1: Normal, 2: High")
    conversation_topic = models.CharField(max_length=512, blank=True, default="")
    has_attachments = models.BooleanField(default=False, db_index=True)
    attachment_count = models.IntegerField(default=0)
    matched_keywords = models.JSONField(default=list)
    risk_score = models.IntegerField(default=0, db_index=True)
    risk_level = models.CharField(max_length=16, default="Low")
    is_flagged = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-sent_date", "-created_at"]
        indexes = [
            models.Index(fields=["mailbox", "-sent_date"]),
            models.Index(fields=["mailbox", "folder_path", "-sent_date"]),
            models.Index(fields=["mailbox", "sender_email", "-sent_date"]),
            models.Index(fields=["mailbox", "has_attachments", "-sent_date"]),
            models.Index(fields=["mailbox", "risk_score", "-sent_date"]),
        ]
        verbose_name = "Email Message"
        verbose_name_plural = "Email Messages"

    def __str__(self) -> str:
        return f"{self.sender_email} -> {self.subject[:50]}"


class EmailAttachment(ForensicBaseModel):
    """
    Physical attachment extracted from an email message.
    """

    email = models.ForeignKey(
        EmailMessage,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    filename = models.CharField(max_length=255)
    file_size_bytes = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=128, blank=True, default="application/octet-stream")
    file_extension = models.CharField(max_length=32, blank=True, default="")
    sha256_hash = models.CharField(max_length=64, db_index=True, help_text="Evidence Hash")
    storage_path = models.CharField(
        max_length=512, blank=True, default="", help_text="Extracted file path"
    )
    is_suspicious = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["filename"]
        verbose_name = "Email Attachment"
        verbose_name_plural = "Email Attachments"

    def __str__(self) -> str:
        return f"{self.filename} ({self.formatted_size})"

    @property
    def formatted_size(self) -> str:
        size = self.file_size_bytes
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB"


class EmailParticipant(ForensicBaseModel):
    """
    Communication counterparty associated with an investigation mailbox.
    """

    mailbox = models.ForeignKey(
        MailboxInvestigation,
        on_delete=models.CASCADE,
        related_name="participants",
    )
    email_address = models.CharField(max_length=255, db_index=True)
    display_name = models.CharField(max_length=255, blank=True, default="")
    sent_count = models.IntegerField(default=0)
    received_count = models.IntegerField(default=0)
    first_interaction = models.DateTimeField(null=True, blank=True)
    last_interaction = models.DateTimeField(null=True, blank=True)
    is_external_domain = models.BooleanField(default=False)

    class Meta:
        ordering = ["-sent_count", "-received_count"]
        unique_together = ("mailbox", "email_address")
        verbose_name = "Email Participant"
        verbose_name_plural = "Email Participants"

    def __str__(self) -> str:
        return f"{self.display_name or self.email_address} (Msgs: {self.sent_count + self.received_count})"
