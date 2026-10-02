"""
Q-Mail Business Logic & Asynchronous Task Orchestration Service
Follows agentic-django principles: pure domain workflows, atomic transactions, and background task dispatch.
"""

import threading
import uuid
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from django.conf import settings
from django.db import connection, transaction
from django.db.models import Q
from loguru import logger

from core.file_uploader import FileUploader

from .backend import PSTStreamParser
from .models import EmailAttachment, EmailMessage, EmailParticipant, MailboxInvestigation


@transaction.atomic
def create_mailbox_investigation(
    *,
    audit_ref: str,
    audit_name: str,
    auditee_name: str,
    auditee_email: str,
    auditee_department: str = "",
    auditee_designation: str = "",
    pst_file_name: str = "",
    file_size_bytes: int = 0,
) -> MailboxInvestigation:
    """
    Initializes a new audit investigation and prepares upload tracking.
    """
    investigation = MailboxInvestigation.objects.create(
        audit_ref=audit_ref.strip(),
        audit_name=audit_name.strip(),
        auditee_name=auditee_name.strip(),
        auditee_email=auditee_email.strip().lower(),
        auditee_department=auditee_department.strip(),
        auditee_designation=auditee_designation.strip(),
        pst_file_name=pst_file_name.strip(),
        file_size_bytes=file_size_bytes,
        status=MailboxInvestigation.IngestionStatus.UPLOADING,
    )
    return investigation


def handle_chunked_upload(
    *,
    mailbox_id: str,
    chunk_index: int,
    total_chunks: int,
    chunk_bytes: bytes,
) -> dict[str, Any]:
    """
    Handles sequential upload chunks for large PST files up to 50+ GB.
    """
    investigation = MailboxInvestigation.objects.get(id=mailbox_id)
    upload_dir = Path(settings.MEDIA_ROOT) / "uploads" / "pst"
    uploader = FileUploader(upload_dir, default_ext=".pst")

    result = uploader.append_chunk(
        upload_id=str(investigation.id),
        chunk_index=chunk_index,
        total_chunks=total_chunks,
        chunk_data=chunk_bytes,
    )

    if result["is_completed"]:
        investigation.pst_file_path = result["file_path"]
        investigation.file_size_bytes = result["current_size_bytes"]
        investigation.file_sha256 = result["file_sha256"]
        investigation.status = MailboxInvestigation.IngestionStatus.PENDING
        investigation.progress_percent = 100.0
        investigation.save(
            update_fields=[
                "pst_file_path",
                "file_size_bytes",
                "file_sha256",
                "status",
                "progress_percent",
                "updated_at",
            ]
        )

    return result


def start_mailbox_processing(mailbox_id: str | uuid.UUID) -> None:
    """
    Launches an asynchronous background worker thread to parse the 50GB PST file.
    """
    investigation = MailboxInvestigation.objects.get(id=mailbox_id)
    if investigation.status == MailboxInvestigation.IngestionStatus.PROCESSING:
        return

    now = datetime.now(UTC)
    investigation.status = MailboxInvestigation.IngestionStatus.PROCESSING
    investigation.is_cancellation_requested = False
    investigation.processing_started_at = now
    investigation.last_heartbeat_at = now
    investigation.error_message = ""
    investigation.save(
        update_fields=[
            "status",
            "is_cancellation_requested",
            "processing_started_at",
            "last_heartbeat_at",
            "error_message",
            "updated_at",
        ]
    )

    # Launch processing in background thread
    worker = threading.Thread(
        target=_execute_pst_ingestion,
        args=(str(investigation.id),),
        daemon=True,
    )
    worker.start()


def cancel_mailbox_processing(mailbox_id: str | uuid.UUID) -> bool:
    """
    Signals the active background worker thread to safely cancel ingestion.
    """
    updated = MailboxInvestigation.objects.filter(
        id=mailbox_id,
        status=MailboxInvestigation.IngestionStatus.PROCESSING,
    ).update(is_cancellation_requested=True)

    if updated:
        logger.info("Cancellation requested for mailbox: {}", mailbox_id)
    return bool(updated)


def recover_stalled_investigations(*, stale_seconds: int = 180) -> int:
    """
    Identifies investigations stuck in PROCESSING state where worker crashed or restarted.
    Marks them as STALLED so the user can easily resume.
    """
    cutoff = datetime.now(UTC) - timedelta(seconds=stale_seconds)
    stalled_qs = MailboxInvestigation.objects.filter(
        status=MailboxInvestigation.IngestionStatus.PROCESSING,
    ).filter(
        Q(last_heartbeat_at__lt=cutoff)
        | Q(last_heartbeat_at__isnull=True, processing_started_at__lt=cutoff)
    )

    count = stalled_qs.update(
        status=MailboxInvestigation.IngestionStatus.STALLED,
        error_message="Background ingestion was interrupted (server reload or worker crash). Click 'Resume Ingestion' to retry.",
    )
    if count > 0:
        logger.warning("Recovered {} stalled investigation tasks.", count)
    return count


def _execute_pst_ingestion(mailbox_id: str) -> None:
    """
    Background worker process: streams pypff messages in batches of 250, inserts into DB.
    Guarantees database connection cleanup and cancellation handling.
    """
    connection.close()
    try:
        investigation = MailboxInvestigation.objects.get(id=mailbox_id)
        if not investigation.pst_file_path or not Path(investigation.pst_file_path).is_file():
            investigation.status = MailboxInvestigation.IngestionStatus.FAILED
            investigation.error_message = (
                f"PST evidence file '{investigation.pst_file_name}' was not found on server disk. "
                "Please upload a valid .pst file through the investigation creation modal."
            )
            investigation.save(update_fields=["status", "error_message", "updated_at"])
            logger.warning("Aborted ingestion for {}: PST file does not exist on disk.", mailbox_id)
            return

        pst_path = Path(investigation.pst_file_path)
        attachments_dir = Path(settings.MEDIA_ROOT) / "attachments" / str(investigation.id)

        # Progress & Heartbeat tracking callback
        def progress_callback(folder_name: str, processed: int, sub_count: int):
            try:
                MailboxInvestigation.objects.filter(id=mailbox_id).update(
                    current_folder=folder_name,
                    processed_messages_count=processed,
                    last_heartbeat_at=datetime.now(UTC),
                )
            except Exception as e:
                logger.debug("Failed to update investigation progress: {}", e)

        def check_cancellation() -> bool:
            return MailboxInvestigation.objects.filter(
                id=mailbox_id, is_cancellation_requested=True
            ).exists()

        parser = PSTStreamParser(
            pst_path=pst_path,
            attachments_dir=attachments_dir,
            progress_callback=progress_callback,
            check_cancellation_callback=check_cancellation,
        )

        message_batch: list[EmailMessage] = []
        attachment_map: list[tuple[int, list[Any]]] = []
        batch_size = 250
        total_attachments = 0
        counterparty_counts: Counter = Counter()

        for parsed_email in parser.parse_messages():
            # Track counterparties
            sender = parsed_email.sender_email.lower()
            if sender:
                counterparty_counts[sender] += 1

            for r in parsed_email.recipients_to + parsed_email.recipients_cc:
                if "@" in r:
                    cleaned_r = r.split("<")[-1].replace(">", "").strip().lower()
                    counterparty_counts[cleaned_r] += 1

            msg_obj = EmailMessage(
                mailbox=investigation,
                message_id=parsed_email.message_id,
                subject=parsed_email.subject or "(No Subject)",
                sender_name=parsed_email.sender_name,
                sender_email=parsed_email.sender_email,
                recipients_to=parsed_email.recipients_to,
                recipients_cc=parsed_email.recipients_cc,
                recipients_bcc=parsed_email.recipients_bcc,
                sent_date=parsed_email.sent_date,
                delivery_date=parsed_email.delivery_date,
                folder_path=parsed_email.folder_path,
                body_plain=parsed_email.body_plain,
                body_html=parsed_email.body_html,
                importance=parsed_email.importance,
                conversation_topic=parsed_email.conversation_topic,
                has_attachments=bool(parsed_email.attachments),
                attachment_count=len(parsed_email.attachments),
            )
            message_batch.append(msg_obj)
            attachment_map.append((len(message_batch) - 1, parsed_email.attachments))

            if len(message_batch) >= batch_size:
                total_attachments += _flush_message_batch(
                    investigation, message_batch, attachment_map
                )
                message_batch.clear()
                attachment_map.clear()

                # Update progress & heartbeat
                MailboxInvestigation.objects.filter(id=mailbox_id).update(
                    processed_messages_count=parser.total_messages_processed,
                    attachment_count=total_attachments,
                    last_heartbeat_at=datetime.now(UTC),
                )

        # Check if parser was cancelled
        if parser.is_cancelled or check_cancellation():
            if message_batch:
                total_attachments += _flush_message_batch(
                    investigation, message_batch, attachment_map
                )
            _build_participants(investigation, counterparty_counts)

            MailboxInvestigation.objects.filter(id=mailbox_id).update(
                status=MailboxInvestigation.IngestionStatus.CANCELLED,
                error_message="Ingestion cancelled by investigator.",
                processed_messages_count=parser.total_messages_processed,
                attachment_count=total_attachments,
                processing_completed_at=datetime.now(UTC),
            )
            logger.info("PST Ingestion cancelled for mailbox: {}", mailbox_id)
            return

        # Flush remaining batch
        if message_batch:
            total_attachments += _flush_message_batch(investigation, message_batch, attachment_map)

        # Build participant summary
        _build_participants(investigation, counterparty_counts)

        # Mark investigation complete
        MailboxInvestigation.objects.filter(id=mailbox_id).update(
            status=MailboxInvestigation.IngestionStatus.COMPLETED,
            progress_percent=100.0,
            processed_messages_count=parser.total_messages_processed,
            attachment_count=total_attachments,
            processing_completed_at=datetime.now(UTC),
            last_heartbeat_at=datetime.now(UTC),
        )
        logger.info("PST Ingestion completed for mailbox: {}", mailbox_id)

    except Exception as e:
        logger.exception("PST Ingestion failed for mailbox: {}", mailbox_id)
        MailboxInvestigation.objects.filter(id=mailbox_id).update(
            status=MailboxInvestigation.IngestionStatus.FAILED,
            error_message=str(e),
            last_heartbeat_at=datetime.now(UTC),
        )
    finally:
        # Prevent thread connection leak
        connection.close()


@transaction.atomic
def _flush_message_batch(
    investigation: MailboxInvestigation,
    message_batch: list[EmailMessage],
    attachment_map: list[tuple[int, list[Any]]],
) -> int:
    """
    Atomically bulk inserts messages and their corresponding attachments.
    """
    created_messages = EmailMessage.objects.bulk_create(message_batch)
    attachment_objects: list[EmailAttachment] = []

    for batch_idx, attachments in attachment_map:
        if not attachments:
            continue
        msg_instance = created_messages[batch_idx]
        for att in attachments:
            attachment_objects.append(
                EmailAttachment(
                    email=msg_instance,
                    filename=att.filename,
                    file_size_bytes=att.file_size_bytes,
                    mime_type=att.mime_type,
                    file_extension=att.file_extension,
                    sha256_hash=att.sha256_hash,
                    storage_path=att.storage_path,
                )
            )

    if attachment_objects:
        EmailAttachment.objects.bulk_create(attachment_objects)

    return len(attachment_objects)


def _build_participants(investigation: MailboxInvestigation, counterparty_counts: Counter) -> None:
    """
    Persists top communication participants for analytics and network graph generation.
    """
    participant_objects = []
    auditee_email_lower = investigation.auditee_email.lower() if investigation.auditee_email else ""
    auditee_domain = (
        auditee_email_lower.split("@")[-1]
        if "@" in auditee_email_lower
        else ""
    )

    # Filter out the auditee themselves from the counterparty list
    if auditee_email_lower in counterparty_counts:
        del counterparty_counts[auditee_email_lower]

    for email_addr, count in counterparty_counts.most_common(100):
        domain = email_addr.split("@")[-1].lower() if "@" in email_addr else ""
        is_external = bool(auditee_domain and domain and domain != auditee_domain)

        participant_objects.append(
            EmailParticipant(
                mailbox=investigation,
                email_address=email_addr,
                display_name=email_addr.split("@")[0],
                sent_count=count,
                received_count=0,
                is_external_domain=is_external,
            )
        )

    if participant_objects:
        EmailParticipant.objects.bulk_create(participant_objects, ignore_conflicts=True)
