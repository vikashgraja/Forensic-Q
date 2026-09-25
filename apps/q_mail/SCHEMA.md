# `q_mail` — Database Schema & ERD Specifications

> [!TIP]
> **dbdiagram.io Compatibility:** Copy and paste the DBML code below directly into [dbdiagram.io](https://dbdiagram.io) to generate visual Entity-Relationship diagrams.

---

## 1. DBML (Database Markup Language for dbdiagram.io)

```dbml
// ==========================================
// Q-Mail Communication Forensics Schema
// dbdiagram.io specification
// ==========================================

Table mailboxes {
  id uuid [pk, default: `uuid4()`]
  custodian_name varchar(255) [not null]
  email_address varchar(255) [not null]
  pst_source_file varchar(255)
  total_messages int [default: 0]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table email_messages {
  id uuid [pk, default: `uuid4()`]
  mailbox_id uuid [ref: > mailboxes.id]
  message_id varchar(255) [db_index: true]
  sent_at timestamp [not null, db_index: true]
  sender varchar(255) [not null]
  recipients_to json [note: 'Array of email strings']
  recipients_cc json [note: 'Array of email strings']
  recipients_bcc json [note: 'Array of email strings']
  subject varchar(500) [not null]
  body_text text
  has_attachments boolean [default: false]
  matched_keywords json [note: 'Array of flagged keywords']
  risk_score int [default: 0]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table email_attachments {
  id uuid [pk, default: `uuid4()`]
  message_id uuid [ref: > email_messages.id]
  filename varchar(255) [not null]
  file_size_bytes bigint [not null]
  sha256_hash varchar(64) [not null]
  mime_type varchar(128)
  is_suspicious boolean [default: false]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}
```

---

## 2. Django ORM Models

```python
from django.db import models
from core.models import ForensicBaseModel


class MailboxCustodian(ForensicBaseModel):
    custodian_name = models.CharField(max_length=255)
    email_address = models.CharField(max_length=255)
    pst_source_file = models.CharField(max_length=255, blank=True)
    total_messages = models.IntegerField(default=0)


class EmailMessage(ForensicBaseModel):
    mailbox = models.ForeignKey(MailboxCustodian, on_delete=models.CASCADE, related_name="messages")
    message_id = models.CharField(max_length=255, db_index=True)
    sent_at = models.DateTimeField(db_index=True)
    sender = models.CharField(max_length=255)
    recipients_to = models.JSONField(default=list)
    recipients_cc = models.JSONField(default=list)
    recipients_bcc = models.JSONField(default=list)
    subject = models.CharField(max_length=500)
    body_text = models.TextField()
    has_attachments = models.BooleanField(default=False)
    matched_keywords = models.JSONField(default=list)
    risk_score = models.IntegerField(default=0)


class EmailAttachment(ForensicBaseModel):
    message = models.ForeignKey(EmailMessage, on_delete=models.CASCADE, related_name="attachments")
    filename = models.CharField(max_length=255)
    file_size_bytes = models.BigIntegerField()
    sha256_hash = models.CharField(max_length=64)
    mime_type = models.CharField(max_length=128)
    is_suspicious = models.BooleanField(default=False)
```
