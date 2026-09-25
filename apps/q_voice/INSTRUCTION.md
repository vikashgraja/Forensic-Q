# `q_voice` — Developer Instructions & Architecture Guide

## 1. Overview & Purpose
`q_voice` is the **Audio & Call Transcript Forensic Engine** of ForensiQ.
It provides:
1. **Audio Ingestion & ASR Transcription:** Automated speech-to-text processing for recorded calls, voicemails, and audio files.
2. **Speaker Diarization & Entity Extraction:** Distinguishing speaker channels and tagging counterparties, amounts, and dates.
3. **Intent & Concealment Detection:** Algorithmic flagging of collusion keywords, coercion, and concealment phrases.

---

## 2. Strict Rules for Interns & Vibe-Coding
* Inherit all models from `core.models.ForensicBaseModel`.
* Use `<c-base>`, `<c-stat_card>`, `<c-filter_bar>`, and `<c-data_grid>`.
