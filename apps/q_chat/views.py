"""
Q-Chat Views & Controllers
Thin presentation controllers coordinating chat selectors, services, and Cotton templates.
"""

from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .selectors import (
    get_all_chat_channels,
    get_chat_channel_by_id,
    get_chat_dashboard_metrics,
    get_chat_participants_summary,
    get_paginated_chat_messages,
)
from .services import delete_chat_channel, ingest_chat_export_file


@require_GET
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """
    Main Q-Chat Instant Messaging Forensics Dashboard.
    """
    metrics = get_chat_dashboard_metrics()
    channels = get_all_chat_channels()

    context = {
        "metrics": metrics,
        "channels": channels,
    }
    return render(request, "q_chat/dashboard.html", context)


@require_GET
def channel_detail_view(request: HttpRequest, channel_id: str) -> HttpResponse:
    """
    Forensic Workspace for a specific Chat Channel.
    Displays interactive message bubbles, participant breakdown, and risk filters.
    """
    channel = get_chat_channel_by_id(channel_id)
    if not channel:
        raise Http404("Chat Channel not found.")

    participants = get_chat_participants_summary(channel.id)

    # Initial page of messages for server-side rendering
    search = request.GET.get("q", "").strip()
    sender = request.GET.get("sender", "").strip()
    flagged_only = request.GET.get("flagged") == "1"
    media_only = request.GET.get("media") == "1"
    deleted_only = request.GET.get("deleted") == "1"
    right_sender = request.GET.get("right", "").strip() or request.GET.get("me", "").strip()
    try:
        threshold = int(request.GET.get("threshold", 75))
    except (ValueError, TypeError):
        threshold = 75
    try:
        page = int(request.GET.get("page", 1))
    except (ValueError, TypeError):
        page = 1
    if page < 1:
        page = 1

    msg_data = get_paginated_chat_messages(
        channel.id,
        page=page,
        page_size=100,
        search=search,
        threshold=threshold,
        sender=sender,
        flagged_only=flagged_only,
        media_only=media_only,
        deleted_only=deleted_only,
        sort_dir="asc",
        right_sender=right_sender,
    )

    context = {
        "channel": channel,
        "participants": participants,
        "messages_data": msg_data,
        "search_query": search,
        "threshold": threshold,
        "selected_sender": sender,
        "flagged_only": flagged_only,
        "media_only": media_only,
        "deleted_only": deleted_only,
        "right_sender": msg_data.get("right_sender", ""),
    }
    return render(request, "q_chat/channel_detail.html", context)


@require_POST
def upload_chat_view(request: HttpRequest) -> HttpResponse:
    """
    Uploads and ingests a chat export file.
    """
    if "chat_file" not in request.FILES:
        messages.error(request, "No chat export file was provided.")
        return redirect("q_chat:dashboard")

    uploaded_file = request.FILES["chat_file"]
    platform = request.POST.get("platform", "WHATSAPP").strip()
    channel_name = request.POST.get("channel_name", "").strip()
    custodian_name = request.POST.get("custodian_name", "").strip()

    from core.profiles import resolve_or_create_profile_from_request

    profile, resolved_name = resolve_or_create_profile_from_request(
        request, default_department="Corporate Communications"
    )
    if profile:
        custodian_name = profile.full_name
    elif not custodian_name and resolved_name:
        custodian_name = resolved_name

    try:
        channel = ingest_chat_export_file(
            file_obj_or_content=uploaded_file,
            filename=uploaded_file.name,
            platform=platform,
            channel_name=channel_name,
            custodian_name=custodian_name,
        )
        messages.success(
            request,
            f"Successfully ingested {channel.total_messages:,} messages into '{channel.channel_name}' ({channel.get_platform_display()}).",
        )
        return redirect("q_chat:channel_detail", channel_id=channel.id)
    except Exception as e:
        messages.error(request, f"Failed to ingest chat export file: {e}")
        return redirect("q_chat:dashboard")


@require_POST
def delete_channel_view(request: HttpRequest, channel_id: str) -> HttpResponse:
    """
    Deletes a chat channel case and all associated messages.
    """
    success = delete_chat_channel(channel_id)
    if success:
        messages.success(request, "Chat channel record deleted successfully.")
    else:
        messages.error(request, "Target chat channel could not be found.")
    return redirect("q_chat:dashboard")


@require_GET
def messages_api_view(request: HttpRequest, channel_id: str) -> JsonResponse:
    """
    JSON endpoint for Tabulator or dynamic stream message loading.
    """
    try:
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("size", 50))
    except (ValueError, TypeError):
        page = 1
        page_size = 50

    search = request.GET.get("search") or request.GET.get("q") or ""
    sender = request.GET.get("sender", "").strip()
    flagged_only = request.GET.get("flagged") in ("1", "true")
    media_only = request.GET.get("media") in ("1", "true")
    deleted_only = request.GET.get("deleted") in ("1", "true")
    sort_dir = request.GET.get("dir", "asc")
    right_sender = request.GET.get("right", "").strip() or request.GET.get("me", "").strip()

    try:
        threshold = int(request.GET.get("threshold", 75))
    except (ValueError, TypeError):
        threshold = 75

    result = get_paginated_chat_messages(
        channel_id,
        page=page,
        page_size=page_size,
        search=search,
        threshold=threshold,
        sender=sender,
        flagged_only=flagged_only,
        media_only=media_only,
        deleted_only=deleted_only,
        sort_dir=sort_dir,
        right_sender=right_sender,
    )
    return JsonResponse(result)
