# `q_chat` — Database Schema & ERD Specifications

> [!TIP]
> **dbdiagram.io Compatibility:** Copy and paste the DBML code below directly into [dbdiagram.io](https://dbdiagram.io) to generate visual Entity-Relationship diagrams.

---

## 1. DBML (Database Markup Language for dbdiagram.io)

```dbml
// ==========================================
// Q-Chat Instant Messaging Forensics Schema
// dbdiagram.io specification
// ==========================================

Table chat_channels {
  id uuid [pk, default: `uuid4()`]
  platform varchar(32) [note: 'Teams, Slack, WhatsApp, Telegram']
  channel_name varchar(255) [not null]
  is_direct_message boolean [default: false]
  participant_count int [default: 2]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table chat_messages {
  id uuid [pk, default: `uuid4()`]
  channel_id uuid [ref: > chat_channels.id]
  sender_name varchar(255) [not null]
  sender_handle varchar(128)
  sent_at timestamp [not null, db_index: true]
  message_text text [not null]
  has_media boolean [default: false]
  media_path varchar(1024)
  is_deleted boolean [default: false]
  is_edited boolean [default: false]
  risk_score int [default: 0]
  flagged_terms json
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}
```

---

## 2. Django ORM Models

```python
from django.db import models
from core.models import ForensicBaseModel


class ChatChannel(ForensicBaseModel):
    platform = models.CharField(max_length=32)
    channel_name = models.CharField(max_length=255)
    is_direct_message = models.BooleanField(default=False)
    participant_count = models.IntegerField(default=2)


class ChatMessage(ForensicBaseModel):
    channel = models.ForeignKey(ChatChannel, on_delete=models.CASCADE, related_name="messages")
    sender_name = models.CharField(max_length=255)
    sender_handle = models.CharField(max_length=128, blank=True)
    sent_at = models.DateTimeField(db_index=True)
    message_text = models.TextField()
    has_media = models.BooleanField(default=False)
    media_path = models.CharField(max_length=1024, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    risk_score = models.IntegerField(default=0)
    flagged_terms = models.JSONField(default=list)
```
