# `q_voice` — Database Schema & ERD Specifications

> [!TIP]
> **dbdiagram.io Compatibility:** Copy and paste the DBML code below directly into [dbdiagram.io](https://dbdiagram.io) to generate visual Entity-Relationship diagrams.

---

## 1. DBML (Database Markup Language for dbdiagram.io)

```dbml
// ==========================================
// Q-Voice Call Transcript Forensics Schema
// dbdiagram.io specification
// ==========================================

Table audio_recordings {
  id uuid [pk, default: `uuid4()`]
  call_ref varchar(64) [not null, unique]
  call_timestamp timestamp [not null]
  duration_seconds int [not null]
  caller_number varchar(32)
  callee_number varchar(32)
  audio_file_path varchar(1024)
  sha256_hash varchar(64)
  transcription_status varchar(32) [default: 'Pending']
  risk_score int [default: 0]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table transcript_segments {
  id uuid [pk, default: `uuid4()`]
  recording_id uuid [ref: > audio_recordings.id]
  speaker_tag varchar(64) [note: 'Speaker 1, Speaker 2, Agent, Client']
  start_time_seconds float [not null]
  end_time_seconds float [not null]
  text_content text [not null]
  detected_intent varchar(64) [note: 'Collusion, Bribery, Pressure, Concealment']
  flagged_keywords json
  confidence_score float [default: 1.0]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}
```

---

## 2. Django ORM Models

```python
from django.db import models
from core.models import ForensicBaseModel


class AudioRecording(ForensicBaseModel):
    call_ref = models.CharField(max_length=64, unique=True, db_index=True)
    call_timestamp = models.DateTimeField(db_index=True)
    duration_seconds = models.IntegerField()
    caller_number = models.CharField(max_length=32, blank=True)
    callee_number = models.CharField(max_length=32, blank=True)
    audio_file_path = models.CharField(max_length=1024)
    sha256_hash = models.CharField(max_length=64)
    transcription_status = models.CharField(max_length=32, default="Pending")
    risk_score = models.IntegerField(default=0)


class TranscriptSegment(ForensicBaseModel):
    recording = models.ForeignKey(AudioRecording, on_delete=models.CASCADE, related_name="segments")
    speaker_tag = models.CharField(max_length=64)
    start_time_seconds = models.FloatField()
    end_time_seconds = models.FloatField()
    text_content = models.TextField()
    detected_intent = models.CharField(max_length=64, blank=True)
    flagged_keywords = models.JSONField(default=list)
    confidence_score = models.FloatField(default=1.0)
```
