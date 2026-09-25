# `q_link` — Developer Instructions & Architecture Guide

## 1. Overview & Purpose
`q_link` is the **Entity Link & Network Graph Correlator Engine** of ForensiQ.
It joins the dots across all other analytical engines by correlating:
1. **Cross-Module Evidence Linking:** Connecting a bank account (`q_bank`) with an email sender (`q_mail`), phone transcript (`q_voice`), and forged invoice (`q_verify`).
2. **Shared Directorships & Relatives:** Identifying common directors, shared addresses, PAN numbers, and shell holding companies.
3. **Graph Network Visualizer:** Interactive node-link graphs displaying fraud syndicates.

---

## 2. Strict Rules for Interns & Vibe-Coding
* Inherit all models from `core.models.ForensicBaseModel`.
* Define edges with bidirectional relationships and confidence scores.
* Use `<c-base>`, `<c-stat_card>`, `<c-chart>`, and `<c-data_grid>`.
