# Project Audit — ShutterSpace

Generated: 11 October 2025

This document summarises a code-level audit mapped to the "Full Stack Individual Capstone Checklist" used for assessment. It lists the status for each Learning Outcome (LO), evidence files, recommended actions, and high-priority next steps.

---

## Summary

Overall status: Mature Django portfolio application with solid data model, forms validation, notifications (polling), and tests. Areas to strengthen: automated JS testing, coverage/CI, explicit role-based permissions (if required), real-time notifications (WebSockets), and explicit AI-attribution of generated code/tests.

---

## LO-by-LO Audit

LO1: Agile Planning & Front-End Design
- Status: Done / Partial
- Evidence:
  - `README.md` wireframes and `docs/readme_images/`
  - `static/css/style.css` (responsive rules)
  - `templates/base.html` uses Bootstrap and semantic HTML
- Notes & Recommendations:
  - Run Lighthouse/axe audits and add results to `TESTING.md`.
  - If you use an Agile tool (Trello/Jira/GitHub Projects), link it in `README.md` for assessors.

LO2: Data Model & Business Logic
- Status: Done
- Evidence:
  - `portfolio/models.py` (Profile, Photo, Comment, Like, Follow, Notification)
  - `portfolio/views.py` (CRUD operations)
  - `migrations/` files show iterative development
- Notes & Recommendations:
  - Consider adding additional unit tests for follow/unfollow edge cases and notification creation race conditions.

LO3: Authentication & Authorization
- Status: Done / Partial
- Evidence:
  - Django auth is used (`register`, login, logout)
  - `@login_required` on sensitive views, object-level checks in delete views
  - `templates/base.html` shows conditional UI for authenticated users
- Notes & Recommendations:
  - If a stricter role model is required, add Groups or a Role field and document it.

LO4: Testing
- Status: Partial
- Evidence:
  - `portfolio/tests.py` (tests for comments, notifications, security)
  - `TESTING.md` references and screenshots
- Notes & Recommendations:
  - Add coverage measurement (coverage.py) and a CI workflow (GitHub Actions) that runs tests and reports coverage.
  - Add JS tests (if critical UI pieces require them).

LO5: Version Control
- Status: Partial / Done
- Evidence:
  - Commits present and descriptive; `README.md` updated and pushed
  - `settings.py` reads `SECRET_KEY` from env
- Notes & Recommendations:
  - Run `git-secrets` or `truffleHog` scan locally and confirm no secrets in history.

LO6: Deployment
- Status: Done / Partial
- Evidence:
  - Heroku references: `Procfile`, `runtime.txt`, `bin/deploy.sh`, and `README.md` steps
  - `DEBUG = False` in `shutterspace/settings.py`
- Notes & Recommendations:
  - Manually verify the production URL and include a screenshot or short smoke-test result in `TESTING.md`.

LO7: Object-Oriented Design
- Status: Done
- Evidence:
  - `portfolio/models.py` implements domain models with constraints (unique_together, CheckConstraint)
- Notes & Recommendations:
  - Document non-obvious model helpers or manager methods if added later.

LO8: AI-Augmented Development
- Status: Partial
- Evidence:
  - `README.md` mentions Copilot and AI tools; tests and some patches suggest AI-assisted work.
- Notes & Recommendations:
  - Add a short table in `README.md` or `AUDIT.md` mapping specific files or tests that were AI-assisted (e.g., `static/css` fixes, tests generation). This helps assessors understand provenance.

---

## High-priority Remediations (recommended)
1. Add CI (GitHub Actions) to run Django tests and measure coverage. Store coverage badge in `README.md`.
2. Run a secrets scan and confirm no API keys or secrets are present in commits.
3. Add Lighthouse/axe accessibility tests to `TESTING.md` and record results.
4. If the LO requires real-time push notifications, consider adding Django Channels and a small WebSocket broadcast for new notifications.
5. Document AI contribution explicitly (which files/tests were AI-assisted) for LO8 transparency.

---

## Suggested next tasks (practical)
- Create `.github/workflows/python-app.yml` to run tests and coverage on push/PR.
- Add a `make test` or `scripts/test.sh` helper to run tests in the virtualenv.
- Add `AUDIT.md` (this file) to the repo (done). Optionally commit & push.

---

If you want, I can now:
- Commit and push `AUDIT.md` to GitHub.
- Create the GitHub Actions workflow for tests/coverage and push it.
- Run a local secret-scan and provide the results.

Tell me which of those you'd like me to do next.