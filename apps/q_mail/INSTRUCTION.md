# `q_mail` — Developer Instructions & Architecture Guide

## 1. Overview & Purpose
`q_mail` is the **PST & Email Communication Forensic Engine** of ForensiQ.
It provides:
1. **PST & EML Ingestion:** High-speed extraction of emails, recipient chains, and attachment metadata.
2. **Keyword & Concept Search:** Regex matching and fraud keyword scoring across email bodies and subject lines.
3. **Communication Network Linking:** Sender-to-recipient interaction matrices and timeline sequencing.

---

## 2. Strict Rules for Interns & Vibe-Coding
* Inherit all models from `core.models.ForensicBaseModel`.
* Use Tabulator with message detail preview modals (`<c-modal>`).
* Format all timestamps in ISO format `YYYY-MM-DD HH:MM:SS`.
