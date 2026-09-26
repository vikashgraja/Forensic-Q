"""
Q-Mail Presentation & View Controllers
Thin views integrating Django Cotton components, Tabulator.js grids, and Plotly charts.
"""

import json
from pathlib import Path

import plotly.express as px
from django.http import FileResponse, Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from loguru import logger

from .models import EmailAttachment, MailboxInvestigation
from .selectors import (
    get_email_detail,
    get_investigation_summary_metrics,
    get_mailbox_progress_state,
    get_paginated_investigation_emails,
    get_top_counterparties,
    list_mailbox_investigations,
)
from .services import (
    create_mailbox_investigation,
    handle_chunked_upload,
    start_mailbox_processing,
)


@require_GET
def investigation_list_view(request: HttpRequest) -> HttpResponse:
    """
    Main Q-Mail Dashboard: Lists all audit mailbox investigations and upload portal.
    """
    investigations = list_mailbox_investigations()

    total_mailboxes = investigations.count()
    completed_count = investigations.filter(
        status=MailboxInvestigation.IngestionStatus.COMPLETED
    ).count()
    processing_count = investigations.filter(
        status=MailboxInvestigation.IngestionStatus.PROCESSING
    ).count()
    total_messages = sum(inv.processed_messages_count for inv in investigations)

    return render(
        request,
        "q_mail/landing.html",
        {
            "investigations": investigations,
            "total_mailboxes": total_mailboxes,
            "completed_count": completed_count,
            "processing_count": processing_count,
            "total_messages": total_messages,
        },
    )


@require_POST
def initiate_upload_view(request: HttpRequest) -> JsonResponse:
    """
    API endpoint to register audit/auditee details prior to chunked PST upload.
    """
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    audit_ref = data.get("audit_ref") or f"AUD-{data.get('auditee_name', 'CASE')[:4].upper()}-2026"
    audit_name = data.get("audit_name", "").strip()
    auditee_name = data.get("auditee_name", "").strip()
    auditee_email = data.get("auditee_email", "").strip()
    auditee_department = data.get("auditee_department", "").strip()
    auditee_designation = data.get("auditee_designation", "").strip()
    pst_file_name = data.get("pst_file_name", "evidence.pst").strip()
    file_size_bytes = int(data.get("file_size_bytes", 0))

    if not (auditee_name and auditee_email):
        return JsonResponse({"error": "Auditee name and email are mandatory fields."}, status=400)

    investigation = create_mailbox_investigation(
        audit_ref=audit_ref,
        audit_name=audit_name or f"Audit of {auditee_name}",
        auditee_name=auditee_name,
        auditee_email=auditee_email,
        auditee_department=auditee_department,
        auditee_designation=auditee_designation,
        pst_file_name=pst_file_name,
        file_size_bytes=file_size_bytes,
    )

    logger.info(
        "Initiated PST investigation {} for auditee {} ({})",
        investigation.audit_ref,
        investigation.auditee_name,
        investigation.auditee_email,
    )

    return JsonResponse(
        {
            "success": True,
            "mailbox_id": str(investigation.id),
            "audit_ref": investigation.audit_ref,
        }
    )


@csrf_exempt
@require_POST
def chunk_upload_view(request: HttpRequest) -> JsonResponse:
    """
    Receives sequential binary chunks for 50GB PST uploads.
    """
    mailbox_id = request.POST.get("mailbox_id")
    chunk_index = int(request.POST.get("chunk_index", 0))
    total_chunks = int(request.POST.get("total_chunks", 1))
    chunk_file = request.FILES.get("chunk")

    if not (mailbox_id and chunk_file):
        return JsonResponse({"error": "Missing mailbox_id or chunk file payload."}, status=400)

    chunk_bytes = chunk_file.read()
    result = handle_chunked_upload(
        mailbox_id=mailbox_id,
        chunk_index=chunk_index,
        total_chunks=total_chunks,
        chunk_bytes=chunk_bytes,
    )

    # Automatically start background ingestion if last chunk uploaded
    if result["is_completed"]:
        start_mailbox_processing(mailbox_id)

    return JsonResponse({"success": True, **result})


@require_POST
def trigger_processing_view(request: HttpRequest, mailbox_id: str) -> JsonResponse:
    """
    Manually triggers or retries PST background processing.
    """
    start_mailbox_processing(mailbox_id)
    return JsonResponse({"success": True, "message": "Background ingestion worker started."})


@require_GET
def progress_api_view(request: HttpRequest, mailbox_id: str) -> JsonResponse:
    """
    Live JSON polling endpoint for progress bar and extraction status.
    """
    state = get_mailbox_progress_state(mailbox_id)
    return JsonResponse(state)


@require_GET
def messages_api_view(request: HttpRequest, mailbox_id: str) -> JsonResponse:
    """
    High-performance paginated API endpoint for Tabulator.js data grid.
    Supports server-side pagination, remote sorting, and multi-field search.
    """
    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("size", 25))
    search = request.GET.get("search", "").strip()
    folder = request.GET.get("folder", "").strip()
    sender = request.GET.get("sender", "").strip()

    has_attachments_val = request.GET.get("has_attachments")
    has_attachments = (
        True
        if has_attachments_val in ("true", "1")
        else (False if has_attachments_val in ("false", "0") else None)
    )

    # Handle Tabulator sort params (e.g. sort[0][field]=sent_date&sort[0][dir]=desc or sort=sent_date)
    sort_field = (
        request.GET.get("sort[0][field]")
        or request.GET.get("sort_by")
        or request.GET.get("sort")
        or "sent_date"
    )
    sort_dir = request.GET.get("sort[0][dir]") or request.GET.get("dir") or "desc"

    result = get_paginated_investigation_emails(
        mailbox_id,
        page=page,
        page_size=page_size,
        search=search,
        folder=folder,
        sender=sender,
        has_attachments=has_attachments,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )

    return JsonResponse(result)


@require_GET
def investigation_detail_view(request: HttpRequest, mailbox_id: str) -> HttpResponse:
    """
    Investigation Workstation: Tabulator.js email grid, Plotly counterparty charts, and evidence filters.
    """
    summary = get_investigation_summary_metrics(mailbox_id)
    inv = summary["investigation"]

    # Plotly Top Counterparties Bar Chart
    top_participants = get_top_counterparties(mailbox_id, limit=8)
    chart_html = ""
    if top_participants:
        fig = px.bar(
            x=[p["count"] for p in top_participants],
            y=[p["display_name"] for p in top_participants],
            orientation="h",
            labels={"x": "Total Messages Exchanged", "y": "Counterparty"},
            color_discrete_sequence=["#a855f7"],  # Purple-500
        )
        fig.update_layout(
            template="plotly_dark",
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter, sans-serif", "color": "#a1a1aa"},
            xaxis={"gridcolor": "#27272a", "linecolor": "#27272a"},
            yaxis={"gridcolor": "#27272a", "linecolor": "#27272a", "autorange": "reversed"},
            height=280,
        )
        chart_html = fig.to_html(full_html=False, include_plotlyjs=False)

    return render(
        request,
        "q_mail/investigation_detail.html",
        {
            "investigation": inv,
            "summary": summary,
            "chart_html": chart_html,
        },
    )


@require_GET
def email_detail_api_view(request: HttpRequest, email_id: str) -> JsonResponse:
    """
    Returns complete email headers, body content, and attachment hashes for the reader drawer.
    """
    email = get_email_detail(email_id)
    attachments_data = [
        {
            "id": str(a.id),
            "filename": a.filename,
            "formatted_size": a.formatted_size,
            "sha256_hash": a.sha256_hash,
            "mime_type": a.mime_type,
            "has_file": bool(a.storage_path and Path(a.storage_path).exists()),
        }
        for a in email.attachments.all()
    ]

    return JsonResponse(
        {
            "id": str(email.id),
            "message_id": email.message_id,
            "subject": email.subject,
            "sender_name": email.sender_name,
            "sender_email": email.sender_email,
            "recipients_to": email.recipients_to,
            "recipients_cc": email.recipients_cc,
            "sent_date": email.sent_date.strftime("%Y-%m-%d %H:%M:%S UTC")
            if email.sent_date
            else "N/A",
            "folder_path": email.folder_path,
            "body_plain": email.body_plain,
            "body_html": email.body_html,
            "has_attachments": email.has_attachments,
            "attachments": attachments_data,
        }
    )


@require_GET
def download_attachment_view(request: HttpRequest, attachment_id: str) -> FileResponse:
    """
    Downloads physical evidence attachment with proper content-disposition.
    """
    attachment = get_object_or_404(EmailAttachment, id=attachment_id)
    if not attachment.storage_path or not Path(attachment.storage_path).exists():
        raise Http404("Physical attachment file not found on disk.")

    return FileResponse(
        open(attachment.storage_path, "rb"),
        as_attachment=True,
        filename=attachment.filename,
    )
