# `q_trail` — Developer Instructions & Architecture Guide

## 1. Overview & Purpose
`q_trail` is the **Multi-Bank Money Trail & Fund Flow Engine** of ForensiQ.
It stitches fragmented transactions across multiple bank accounts to reveal:
1. **Pass-Through & Layering Paths:** Detects fund movements that enter and exit accounts within minutes to obscure origin.
2. **Circular Round-Tripping Loops:** Identifies funds returning to the originator via shell entities or 3rd-party escrow intermediaries.
3. **Interactive Flow Visualizers:** Powered by Plotly Sankey diagrams and Tabulator path tables.

---

## 2. Strict Rules for Interns & Vibe-Coding
* Inherit all models from `core.models.ForensicBaseModel`.
* Use Plotly with `template="plotly_dark"` and transparent background (`plot_bgcolor="rgba(0,0,0,0)"`).
* Use `<c-base>`, `<c-stat_card>`, `<c-chart>`, and `<c-data_grid>` Cotton tags.
