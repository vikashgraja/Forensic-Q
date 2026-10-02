"""
Q-Chat Parser & Forensic Screener Backend
Parses WhatsApp (.txt/.zip), Microsoft Teams / Slack (JSON/CSV), and Telegram exports.
Extracts message streams, timestamps, participants, media attachments, and risk flags.
"""

import csv
import io
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_CHAT_WATCHLIST = [
    ("cash", 70, "Bribery & Kickbacks"),
    ("commission", 60, "Bribery & Kickbacks"),
    ("bribe", 95, "Bribery & Kickbacks"),
    ("cut", 50, "Bribery & Kickbacks"),
    ("kickback", 95, "Bribery & Kickbacks"),
    ("hawala", 90, "Illicit Finance"),
    ("personal account", 80, "Off-Channel Payment"),
    ("gpay", 50, "Off-Channel Payment"),
    ("phonepe", 50, "Off-Channel Payment"),
    ("delete", 65, "Concealment"),
    ("clear chat", 75, "Concealment"),
    ("off the record", 85, "Concealment"),
    ("dont email", 80, "Concealment"),
    ("call me", 40, "Off-Channel Comms"),
    ("whatsapp only", 75, "Off-Channel Comms"),
    ("quote", 40, "Bid Rigging"),
    ("discount", 45, "Commercial Terms"),
    ("margin", 45, "Commercial Terms"),
    ("tender", 50, "Procurement"),
    ("l1", 60, "Bid Rigging"),
    ("competitor", 55, "Bid Rigging"),
    ("inside info", 90, "Collusion"),
    ("gift", 60, "Bribery & Kickbacks"),
]


def screen_message_text(
    text: str, custom_watchlist: list[tuple[str, int, str]] | None = None
) -> tuple[int, list[str]]:
    """
    Screens message text against forensic keywords.
    Returns (risk_score, flagged_terms).
    """
    if not text:
        return 0, []

    watchlist = custom_watchlist or DEFAULT_CHAT_WATCHLIST
    text_lower = text.lower()
    flagged = []
    total_score = 0

    for term, weight, _cat in watchlist:
        # Match word boundaries or exact phrases
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, text_lower):
            flagged.append(term)
            total_score += weight

    risk_score = min(100, total_score)
    return risk_score, flagged


SYSTEM_MESSAGE_INDICATORS = [
    "end-to-end encrypted",
    "end-to-end encryption",
    "secured with end-to-end encryption",
    "is a contact.",
    "is a contact",
    "is not in your contacts",
    "added to your contacts",
    "tap to view contact details",
    "security code changed",
    "your security code with",
    "this chat is with an official business account",
    "this chat is with a business account",
    "created group",
    "added you to",
    "changed the group description",
    "changed this group's icon",
    "changed the subject to",
    "left the group",
    "removed from the group",
    "you're now an admin",
    "disappearing messages were turned",
    "waiting for this message. this may take a while",
]


def is_whatsapp_system_message(text: str) -> bool:
    """
    Detects automated WhatsApp disclaimer, security, encryption, and contact notification banners.
    """
    if not text:
        return False
    # Strip invisible unicode formatting marks
    clean = text.replace("\u200e", "").replace("\u200f", "").strip().lower()
    return any(indicator in clean for indicator in SYSTEM_MESSAGE_INDICATORS)


# WhatsApp Timestamp Patterns with Sender (colon separated)
WHATSAPP_PATTERNS = [
    # 24/04/2024, 14:32 - Sender: Message
    re.compile(
        r"^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[apAP][mM])?)\s*[-–]\s*(.*?):\s*(.*)$"
    ),
    # [24/04/24, 14:32:10] Sender: Message
    re.compile(
        r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[apAP][mM])?)\]\s*(.*?):\s*(.*)$"
    ),
    # 24.04.2024, 14:32 - Sender: Message
    re.compile(
        r"^(\d{1,2}\.\d{1,2}\.\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[apAP][mM])?)\s*[-–]\s*(.*?):\s*(.*)$"
    ),
]

# WhatsApp Timestamp Patterns WITHOUT Sender (System disclaimers)
WHATSAPP_SYSTEM_PATTERNS = [
    # 24/04/2024, 14:32 - System message
    re.compile(
        r"^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[apAP][mM])?)\s*[-–]\s*(.*)$"
    ),
    # [24/04/24, 14:32:10] System message
    re.compile(
        r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[apAP][mM])?)\]\s*(.*)$"
    ),
    # 24.04.2024, 14:32 - System message
    re.compile(
        r"^(\d{1,2}\.\d{1,2}\.\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[apAP][mM])?)\s*[-–]\s*(.*)$"
    ),
]


def parse_whatsapp_datetime(date_str: str, time_str: str) -> datetime:
    """
    Parses various date and time format variations found in WhatsApp exports.
    """
    date_str = date_str.replace(".", "/").replace("-", "/").strip()
    time_str = time_str.strip()

    date_formats = ["%d/%m/%Y", "%d/%m/%y", "%m/%d/%Y", "%m/%d/%y"]
    time_formats = ["%H:%M:%S", "%H:%M", "%I:%M:%S %p", "%I:%M %p", "%I:%M%p"]

    for df in date_formats:
        for tf in time_formats:
            try:
                dt_str = f"{date_str} {time_str}"
                dt = datetime.strptime(dt_str, f"{df} {tf}")
                return dt.replace(tzinfo=UTC)
            except ValueError:
                continue

    # Fallback to current UTC time if unparseable
    return datetime.now(UTC)


def parse_whatsapp_export(content: str) -> list[dict[str, Any]]:
    """
    Parses a raw WhatsApp exported text file into structured messages.
    Supports multi-line messages, media attachment tags, and deleted flags.
    Recognizes system disclaimers and separates them from user chat bubbles.
    """
    lines = content.splitlines()
    messages: list[dict[str, Any]] = []
    current_msg: dict[str, Any] | None = None

    for line in lines:
        line_clean = line.strip().replace("\u200e", "").replace("\u200f", "")
        if not line_clean:
            continue

        matched = False
        # 1. Try standard pattern (with sender and colon)
        for pat in WHATSAPP_PATTERNS:
            m = pat.match(line_clean)
            if m:
                matched = True
                if current_msg:
                    messages.append(current_msg)

                date_part, time_part, sender_part, text_part = m.groups()
                dt = parse_whatsapp_datetime(date_part, time_part)
                sender = sender_part.strip()
                text = text_part.strip()

                # Check if this message is actually a system/disclaimer message
                is_system = is_whatsapp_system_message(text) or is_whatsapp_system_message(sender)
                if is_system:
                    sender = "System"

                # Detect media attachments
                has_media = False
                media_type = "NONE"
                media_fn = ""
                if "<Media omitted>" in text or "image omitted" in text:
                    has_media = True
                    media_type = "IMAGE"
                elif "(file attached)" in text or "document omitted" in text:
                    has_media = True
                    media_type = "DOCUMENT"
                    fn_match = re.search(
                        r"(\S+\.(?:pdf|docx|xlsx|jpg|png|zip))", text, re.IGNORECASE
                    )
                    if fn_match:
                        media_fn = fn_match.group(1)
                elif "audio omitted" in text or "voice note omitted" in text:
                    has_media = True
                    media_type = "AUDIO"

                # Detect deleted message markers
                is_deleted = False
                if (
                    "This message was deleted" in text
                    or "You deleted this message" in text
                    or "This message was deleted by" in text
                ):
                    is_deleted = True

                score, flagged = (0, []) if is_system else screen_message_text(text)

                current_msg = {
                    "sender_name": sender,
                    "sender_handle": "",
                    "sent_at": dt,
                    "message_text": text,
                    "has_media": has_media,
                    "media_type": media_type,
                    "media_filename": media_fn,
                    "is_deleted": is_deleted,
                    "is_edited": False,
                    "is_system": is_system,
                    "risk_score": score,
                    "flagged_terms": flagged,
                }
                break

        # 2. Try system pattern (timestamped system lines without sender colon)
        if not matched:
            for pat in WHATSAPP_SYSTEM_PATTERNS:
                m = pat.match(line_clean)
                if m:
                    date_part, time_part, text_part = m.groups()
                    text = text_part.strip()
                    if is_whatsapp_system_message(text):
                        matched = True
                        if current_msg:
                            messages.append(current_msg)

                        dt = parse_whatsapp_datetime(date_part, time_part)
                        current_msg = {
                            "sender_name": "System",
                            "sender_handle": "",
                            "sent_at": dt,
                            "message_text": text,
                            "has_media": False,
                            "media_type": "NONE",
                            "media_filename": "",
                            "is_deleted": False,
                            "is_edited": False,
                            "is_system": True,
                            "risk_score": 0,
                            "flagged_terms": [],
                        }
                        break

        # 3. Check for standalone un-timestamped system banner at the top of file
        if not matched and not current_msg and is_whatsapp_system_message(line_clean):
            current_msg = {
                "sender_name": "System",
                "sender_handle": "",
                "sent_at": datetime.now(UTC),
                "message_text": line_clean,
                "has_media": False,
                "media_type": "NONE",
                "media_filename": "",
                "is_deleted": False,
                "is_edited": False,
                "is_system": True,
                "risk_score": 0,
                "flagged_terms": [],
            }
            messages.append(current_msg)
            current_msg = None
            continue

        # 4. Continuation of previous message (multi-line message)
        if not matched and current_msg:
            current_msg["message_text"] += "\n" + line_clean
            if not current_msg.get("is_system"):
                score, flagged = screen_message_text(current_msg["message_text"])
                current_msg["risk_score"] = score
                current_msg["flagged_terms"] = flagged

    if current_msg:
        messages.append(current_msg)

    return messages


def parse_json_export(content: str) -> list[dict[str, Any]]:
    """
    Parses JSON chat exports (Teams, Slack, Telegram).
    """
    data = json.loads(content)
    messages: list[dict[str, Any]] = []

    raw_items = data.get("messages", data) if isinstance(data, dict) else data
    if not isinstance(raw_items, list):
        return messages

    for item in raw_items:
        sender = (
            item.get("sender_name")
            or item.get("from")
            or item.get("user")
            or item.get("author")
            or "Unknown"
        )
        text = (
            item.get("message_text")
            or item.get("text")
            or item.get("body")
            or item.get("content")
            or ""
        )
        if isinstance(text, list):
            # Telegram rich text blocks
            text = " ".join(t.get("text", "") if isinstance(t, dict) else str(t) for t in text)

        date_val = (
            item.get("sent_at") or item.get("date") or item.get("timestamp") or item.get("ts")
        )
        if isinstance(date_val, (int, float)):
            # Unix timestamp
            dt = datetime.fromtimestamp(date_val, tz=UTC)
        elif isinstance(date_val, str):
            try:
                dt = datetime.fromisoformat(date_val.replace("Z", "+00:00"))
            except ValueError:
                dt = datetime.now(UTC)
        else:
            dt = datetime.now(UTC)

        is_system = is_whatsapp_system_message(text) or sender.lower() in ("system", "whatsapp")
        if is_system:
            sender = "System"
            score, flagged = 0, []
        else:
            score, flagged = screen_message_text(text)

        has_media = bool(
            item.get("has_media")
            or item.get("file")
            or item.get("media_type")
            or item.get("attachments")
        )
        media_type = item.get("media_type") or ("DOCUMENT" if has_media else "NONE")

        messages.append(
            {
                "sender_name": sender,
                "sender_handle": item.get("sender_handle") or item.get("from_id") or "",
                "sent_at": dt,
                "message_text": text,
                "has_media": has_media,
                "media_type": media_type,
                "media_filename": item.get("file_name") or "",
                "is_deleted": bool(item.get("is_deleted")),
                "is_edited": bool(item.get("is_edited") or item.get("edited")),
                "is_system": is_system,
                "risk_score": score,
                "flagged_terms": flagged,
            }
        )

    return messages


def parse_csv_export(content: str) -> list[dict[str, Any]]:
    """
    Parses CSV chat exports.
    """
    reader = csv.DictReader(io.StringIO(content))
    messages: list[dict[str, Any]] = []

    for row in reader:
        # Find column names case-insensitively
        row_norm = {k.strip().lower(): v for k, v in row.items() if k}
        sender = (
            row_norm.get("sender")
            or row_norm.get("sender_name")
            or row_norm.get("user")
            or row_norm.get("from")
            or "Unknown"
        )
        text = (
            row_norm.get("message")
            or row_norm.get("text")
            or row_norm.get("content")
            or row_norm.get("body")
            or ""
        )
        date_str = (
            row_norm.get("date")
            or row_norm.get("timestamp")
            or row_norm.get("sent_at")
            or row_norm.get("time")
            or ""
        )

        try:
            dt = datetime.fromisoformat(date_str)
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=UTC)
        except (ValueError, TypeError):
            dt = datetime.now(UTC)

        is_system = is_whatsapp_system_message(text) or sender.lower() in ("system", "whatsapp")
        if is_system:
            sender = "System"
            score, flagged = 0, []
        else:
            score, flagged = screen_message_text(text)

        messages.append(
            {
                "sender_name": sender,
                "sender_handle": row_norm.get("handle") or row_norm.get("phone") or "",
                "sent_at": dt,
                "message_text": text,
                "has_media": bool(
                    row_norm.get("has_media")
                    and row_norm.get("has_media").lower() in ("true", "1", "yes")
                ),
                "media_type": row_norm.get("media_type") or "NONE",
                "media_filename": row_norm.get("filename") or "",
                "is_deleted": bool(
                    row_norm.get("is_deleted")
                    and row_norm.get("is_deleted").lower() in ("true", "1", "yes")
                ),
                "is_edited": bool(
                    row_norm.get("is_edited")
                    and row_norm.get("is_edited").lower() in ("true", "1", "yes")
                ),
                "is_system": is_system,
                "risk_score": score,
                "flagged_terms": flagged,
            }
        )

    return messages


def ingest_chat_file(file_content: str, filename: str) -> list[dict[str, Any]]:
    """
    Master file router for chat ingestion.
    """
    ext = Path(filename).suffix.lower()

    if ext == ".json":
        return parse_json_export(file_content)
    elif ext == ".csv":
        return parse_csv_export(file_content)
    else:
        # Default to WhatsApp / text format
        return parse_whatsapp_export(file_content)
