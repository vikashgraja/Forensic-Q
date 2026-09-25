# `q_chat` — Developer Instructions & Architecture Guide

## 1. Overview & Purpose
`q_chat` is the **Corporate Chat & Instant Messaging Forensic Engine** of ForensiQ.
It provides:
1. **Chat Ingestion:** Parsing JSON/CSV exports from Microsoft Teams, Slack, WhatsApp Business, and Telegram.
2. **Channel & Thread Reconstruction:** Restoring full chat threads, replies, reactions, and shared media files.
3. **Keyword & Topic Triage:** Flagging off-channel discussions, collusion keywords, and deleted message artifacts.

---

## 2. Strict Rules for Interns & Vibe-Coding
* Inherit all models from `core.models.ForensicBaseModel`.
* Use `<c-base>`, `<c-stat_card>`, `<c-filter_bar>`, and `<c-data_grid>`.
