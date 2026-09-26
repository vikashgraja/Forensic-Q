"""
Q-Mail Read-Only Selectors Layer
Follows agentic-django principles: zero DB mutations, proactive N+1 elimination with select_related & prefetch_related.
"""

import uuid
from typing import Any

from django.db.models import Count, Max, Min, Q, QuerySet
from django.shortcuts import get_object_or_404

from .models import EmailAttachment, EmailMessage, EmailParticipant, MailboxInvestigation


def list_mailbox_investigations() -> QuerySet[MailboxInvestigation]:
    """
    Returns all audit mailbox investigations ordered by creation date.
    """
    return MailboxInvestigation.objects.all().order_by("-created_at")


def get_mailbox_investigation(mailbox_id: str | uuid.UUID) -> MailboxInvestigation:
    """
    Retrieves a single mailbox investigation instance.
    """
    return get_object_or_404(MailboxInvestigation, id=mailbox_id)


def get_mailbox_progress_state(mailbox_id: str | uuid.UUID) -> dict[str, Any]:
    """
    Fetches real-time ingestion state for live UI polling.
    """
    inv = get_object_or_404(MailboxInvestigation, id=mailbox_id)
    return {
        "id": str(inv.id),
        "audit_ref": inv.audit_ref,
        "auditee_name": inv.auditee_name,
        "status": inv.status,
        "status_display": inv.get_status_display(),
        "progress_percent": round(inv.progress_percent, 1),
        "processed_messages_count": inv.processed_messages_count,
        "attachment_count": inv.attachment_count,
        "current_folder": inv.current_folder,
        "error_message": inv.error_message,
        "is_active": inv.status
        in (
            MailboxInvestigation.IngestionStatus.UPLOADING,
            MailboxInvestigation.IngestionStatus.PROCESSING,
        ),
    }


def get_investigation_emails(
    mailbox_id: str | uuid.UUID,
    *,
    search: str = "",
    folder: str = "",
    sender: str = "",
    has_attachments: bool | None = None,
    min_risk: int = 0,
    limit: int = 2000,
) -> QuerySet[EmailMessage]:
    """
    Fetches email messages with pre-fetched attachments to eliminate N+1 queries.
    """
    qs = (
        EmailMessage.objects.filter(mailbox_id=mailbox_id)
        .select_related("mailbox")
        .prefetch_related("attachments")
        .order_by("-sent_date")
    )

    if search:
        qs = qs.filter(
            Q(subject__icontains=search)
            | Q(sender_email__icontains=search)
            | Q(sender_name__icontains=search)
            | Q(body_plain__icontains=search)
        )

    if folder:
        qs = qs.filter(folder_path=folder)

    if sender:
        qs = qs.filter(sender_email__icontains=sender)

    if has_attachments is not None:
        qs = qs.filter(has_attachments=has_attachments)

    if min_risk > 0:
        qs = qs.filter(risk_score__gte=min_risk)

    return qs[:limit]


def get_paginated_investigation_emails(
    mailbox_id: str | uuid.UUID,
    *,
    page: int = 1,
    page_size: int = 25,
    search: str = "",
    folder: str = "",
    sender: str = "",
    has_attachments: bool | None = None,
    min_risk: int = 0,
    sort_field: str = "sent_date",
    sort_dir: str = "desc",
) -> dict[str, Any]:
    """
    High-performance server-side paginated selector for Tabulator.js grid.
    Scales effortlessly across 500,000+ emails with fast indexing and low memory usage.
    """
    from django.core.paginator import Paginator

    qs = EmailMessage.objects.filter(mailbox_id=mailbox_id).prefetch_related("attachments")

    if search:
        qs = qs.filter(
            Q(subject__icontains=search)
            | Q(sender_email__icontains=search)
            | Q(sender_name__icontains=search)
            | Q(body_plain__icontains=search)
        )

    if folder:
        qs = qs.filter(folder_path=folder)

    if sender:
        qs = qs.filter(sender_email__icontains=sender)

    if has_attachments is not None:
        qs = qs.filter(has_attachments=has_attachments)

    if min_risk > 0:
        qs = qs.filter(risk_score__gte=min_risk)

    # Safe sort mapping
    allowed_sort_fields = {
        "sent_date": "sent_date",
        "sender": "sender_email",
        "subject": "subject",
        "folder": "folder_path",
        "attachment_count": "attachment_count",
        "risk_score": "risk_score",
    }
    db_sort_field = allowed_sort_fields.get(sort_field, "sent_date")
    order_prefix = "-" if sort_dir.lower() == "desc" else ""
    qs = qs.order_by(f"{order_prefix}{db_sort_field}", "-created_at")

    paginator = Paginator(qs, max(1, min(page_size, 500)))
    page_obj = paginator.get_page(page)

    rows = []
    for m in page_obj.object_list:
        rows.append(
            {
                "id": str(m.id),
                "sent_date": m.sent_date.strftime("%Y-%m-%d %H:%M") if m.sent_date else "N/A",
                "sender": m.sender_name or m.sender_email,
                "sender_email": m.sender_email,
                "subject": m.subject,
                "folder": m.folder_path.split("/")[-1] if m.folder_path else "Inbox",
                "has_attachments": m.has_attachments,
                "attachment_count": m.attachment_count,
                "risk_score": m.risk_score,
                "risk_level": m.risk_level,
            }
        )

    return {
        "data": rows,
        "last_page": paginator.num_pages,
        "last_row": paginator.count,
        "total_count": paginator.count,
        "current_page": page_obj.number,
    }


def get_email_detail(email_id: str | uuid.UUID) -> EmailMessage:
    """
    Retrieves full email details with all attachments.
    """
    return get_object_or_404(
        EmailMessage.objects.select_related("mailbox").prefetch_related("attachments"),
        id=email_id,
    )


def get_investigation_summary_metrics(mailbox_id: str | uuid.UUID) -> dict[str, Any]:
    """
    Aggregates high-level metrics across the investigation.
    """
    inv = get_object_or_404(MailboxInvestigation, id=mailbox_id)
    email_stats = EmailMessage.objects.filter(mailbox=inv).aggregate(
        total_emails=Count("id"),
        earliest_sent=Min("sent_date"),
        latest_sent=Max("sent_date"),
        with_attachments=Count("id", filter=Q(has_attachments=True)),
    )
    attachment_total = EmailAttachment.objects.filter(email__mailbox=inv).count()

    folders = list(
        EmailMessage.objects.filter(mailbox=inv).values_list("folder_path", flat=True).distinct()
    )

    return {
        "investigation": inv,
        "total_emails": email_stats["total_emails"] or 0,
        "total_attachments": attachment_total,
        "earliest_sent": email_stats["earliest_sent"],
        "latest_sent": email_stats["latest_sent"],
        "with_attachments": email_stats["with_attachments"] or 0,
        "folders": [f for f in folders if f],
    }


def get_top_counterparties(mailbox_id: str | uuid.UUID, limit: int = 10) -> list[dict[str, Any]]:
    """
    Returns top counterparties for Plotly chart visualization.
    """
    participants = EmailParticipant.objects.filter(mailbox_id=mailbox_id).order_by("-sent_count")[
        :limit
    ]
    return [
        {
            "email": p.email_address,
            "display_name": p.display_name or p.email_address.split("@")[0],
            "count": p.sent_count,
            "is_external": p.is_external_domain,
        }
        for p in participants
    ]
