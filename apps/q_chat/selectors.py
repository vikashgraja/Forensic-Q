"""
Q-Chat Forensic Selectors
Query, compute, and aggregate corporate chat conversations, message streams, and collusion indicators.
"""

import uuid
from typing import Any

from django.core.paginator import Paginator
from django.db.models import Count, Max, Min, Q, QuerySet

from .backend.chat_parser import is_whatsapp_system_message
from .models import ChatChannel, ChatMessage


def get_chat_dashboard_metrics() -> dict[str, Any]:
    """
    Computes global metrics for the Q-Chat dashboard.
    """
    total_channels = ChatChannel.objects.count()
    total_messages = ChatMessage.objects.count()
    flagged_messages = ChatMessage.objects.filter(risk_score__gte=50).count()
    deleted_messages = ChatMessage.objects.filter(is_deleted=True).count()
    media_messages = ChatMessage.objects.filter(has_media=True).count()

    platforms = (
        ChatChannel.objects.values("platform")
        .annotate(channel_count=Count("id"), msg_count=Count("messages"))
        .order_by("-msg_count")
    )

    top_flagged_senders = list(
        ChatMessage.objects.filter(risk_score__gte=50)
        .exclude(sender_name__in=["System", "system", "WhatsApp", "whatsapp"])
        .values("sender_name")
        .annotate(flagged_count=Count("id"))
        .order_by("-flagged_count")[:6]
    )

    return {
        "total_channels": total_channels,
        "total_messages": total_messages,
        "flagged_messages": flagged_messages,
        "deleted_messages": deleted_messages,
        "media_messages": media_messages,
        "platforms": list(platforms),
        "top_flagged_senders": top_flagged_senders,
    }


def get_all_chat_channels() -> QuerySet[ChatChannel]:
    """
    Retrieves all chat channels ordered by most recent message.
    """
    return ChatChannel.objects.all().order_by("-last_message_at", "-created_at")


def get_chat_channel_by_id(channel_id: str | uuid.UUID) -> ChatChannel | None:
    """
    Retrieves a single channel by primary key.
    """
    try:
        return ChatChannel.objects.get(id=channel_id)
    except (ChatChannel.DoesNotExist, ValueError):
        return None


def get_paginated_chat_messages(
    channel_id: str | uuid.UUID,
    *,
    page: int = 1,
    page_size: int = 50,
    search: str = "",
    sender: str = "",
    flagged_only: bool = False,
    media_only: bool = False,
    deleted_only: bool = False,
    sort_dir: str = "asc",  # 'asc' for chronological chat stream, 'desc' for latest first
    right_sender: str = "",
) -> dict[str, Any]:
    """
    Retrieves paginated messages for a specific channel with flexible filters.
    Consistently assigns left vs right side per participant, and isolates system disclaimers.
    """
    qs = ChatMessage.objects.filter(channel_id=channel_id)

    if search:
        s = search.strip()
        qs = qs.filter(Q(message_text__icontains=s) | Q(sender_name__icontains=s))

    if sender:
        qs = qs.filter(sender_name__iexact=sender.strip())

    if flagged_only:
        qs = qs.filter(risk_score__gte=50)

    if media_only:
        qs = qs.filter(has_media=True)

    if deleted_only:
        qs = qs.filter(is_deleted=True)

    order_prefix = "-" if sort_dir.lower() == "desc" else ""
    qs = qs.order_by(f"{order_prefix}sent_at", f"{order_prefix}created_at")

    # Determine which participant should appear on the right side
    if not right_sender:
        try:
            channel = ChatChannel.objects.get(id=channel_id)
            # 1. Check if channel custodian matches a participant
            if channel.custodian_name:
                cust_clean = channel.custodian_name.strip().lower()
                for p in channel.participants:
                    if p.strip().lower() == cust_clean or cust_clean in p.strip().lower():
                        right_sender = p
                        break

            # 2. If no custodian match, pick 2nd participant in chronological appearance
            if not right_sender:
                first_senders = list(
                    ChatMessage.objects.filter(channel_id=channel_id)
                    .exclude(sender_name__in=["System", "system", "WhatsApp", "whatsapp"])
                    .order_by("sent_at", "created_at")
                    .values_list("sender_name", flat=True)
                )
                ordered_participants: list[str] = []
                for s_name in first_senders:
                    if (
                        s_name
                        and s_name not in ordered_participants
                        and not is_whatsapp_system_message(s_name)
                    ):
                        ordered_participants.append(s_name)

                if len(ordered_participants) >= 2:
                    # In standard chat view: Person 1 is on the left (initiator/contact),
                    # Person 2 is on the right (responder/account holder)
                    right_sender = ordered_participants[1]
        except Exception:
            right_sender = ""

    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)

    rows = []
    for msg in page_obj:
        is_sys = (
            msg.sender_name.lower() in ("system", "whatsapp")
            or (isinstance(msg.raw_payload, dict) and msg.raw_payload.get("is_system", False))
            or is_whatsapp_system_message(msg.message_text)
            or is_whatsapp_system_message(msg.sender_name)
        )
        is_right = (
            (not is_sys)
            and bool(right_sender)
            and (msg.sender_name.strip().lower() == right_sender.strip().lower())
        )

        rows.append(
            {
                "id": str(msg.id),
                "sender_name": "System" if is_sys else msg.sender_name,
                "sender_handle": msg.sender_handle,
                "sent_at": msg.sent_at.strftime("%d %b %Y, %H:%M:%S") if msg.sent_at else "-",
                "sent_time": msg.sent_at.strftime("%H:%M") if msg.sent_at else "-",
                "sent_date": msg.sent_at.strftime("%d %b %Y") if msg.sent_at else "-",
                "message_text": msg.message_text,
                "has_media": msg.has_media,
                "media_type": msg.media_type,
                "media_filename": msg.media_filename,
                "is_deleted": msg.is_deleted,
                "is_edited": msg.is_edited,
                "risk_score": 0 if is_sys else msg.risk_score,
                "flagged_terms": [] if is_sys else msg.flagged_terms,
                "is_system": is_sys,
                "is_right_side": is_right,
            }
        )

    return {
        "data": rows,
        "total_count": paginator.count,
        "last_page": paginator.num_pages,
        "current_page": page_obj.number,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        "previous_page": page_obj.previous_page_number() if page_obj.has_previous() else None,
        "page_range": list(paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)) if paginator.num_pages > 1 else [1],
        "right_sender": right_sender,
    }


def get_chat_participants_summary(channel_id: str | uuid.UUID) -> list[dict[str, Any]]:
    """
    Summarizes participants in a channel with message counts and flagged message counts.
    Excludes automated system and disclaimer messages.
    """
    raw_participants = (
        ChatMessage.objects.filter(channel_id=channel_id)
        .exclude(sender_name__in=["System", "system", "WhatsApp", "whatsapp"])
        .values("sender_name")
        .annotate(
            total_msgs=Count("id"),
            flagged_msgs=Count("id", filter=Q(risk_score__gte=50)),
            deleted_msgs=Count("id", filter=Q(is_deleted=True)),
            first_seen=Min("sent_at"),
            last_seen=Max("sent_at"),
        )
        .order_by("-total_msgs")
    )

    results = []
    for p in raw_participants:
        # Ignore if sender name itself looks like a system notice
        if is_whatsapp_system_message(p["sender_name"]):
            continue

        results.append(
            {
                "sender_name": p["sender_name"],
                "total_msgs": p["total_msgs"],
                "flagged_msgs": p["flagged_msgs"],
                "deleted_msgs": p["deleted_msgs"],
                "first_seen": p["first_seen"].strftime("%d %b %Y") if p["first_seen"] else "-",
                "last_seen": p["last_seen"].strftime("%d %b %Y") if p["last_seen"] else "-",
            }
        )
    return results
