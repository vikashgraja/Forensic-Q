# `core` — User & Operations Guide

## 1. Accessing the Platform

### Master Portal Authorization
1. Navigate to the workstation root: `http://127.0.0.1:8000/`
2. If unauthenticated, the workstation automatically redirects to the authorization portal: `http://127.0.0.1:8000/login/`
3. Enter the session authorization key (Default: `forensiq2026`).
4. Click **Authorize Session** (or press Enter).
5. Upon successful validation, you are redirected to the **Investigation Platform** landing dashboard.

---

## 2. Navigating the Investigation Platform

The landing page displays all active forensic analytical engines organized in high-contrast visual cards:

* **Live Engines (`LIVE`):** Fully operational modules with interactive ledgers, visualizers, and audit tables.
* **Pipeline Engines (`BUILDING`):** Scheduled analytical modules currently under development.
* **Launching a Module:** Click anywhere on an engine card to launch its dedicated investigation workspace.

---

## 3. Session Locking & Security

* **Locking the Workstation:** To lock your session and protect forensic data, click the **Lock** button on the top right navigation bar.
* **Theme Switching:** Toggle between Dark Mode and Light Mode at any time using the Sun/Moon button on the top right. Your theme preference is preserved across browser sessions.
