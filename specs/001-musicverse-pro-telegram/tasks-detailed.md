Detailed Tasks: MusicVerse PRO — Telegram Mini App Integration
Feature: specs/001-musicverse-pro-telegram/spec.md
Created: 2025-12-02T04:22:09Z

Purpose
Provide a granular breakdown of tasks (subtasks), estimates, explicit file targets, dependencies and acceptance criteria for developer assignment and sprint planning.

Legend
- ID format: Txxx.y (parent.child)
- [P] parallelizable
- Estimate: LO = low (0.5-1d), MD = medium (1-3d), HI = high (3-8d)
- Owner: placeholder for assignment

PHASE 0 — Foundations

T001 Init repo skeleton and CI
- T001.1 Create repository layout and README (LO). Files: README.md, .gitignore. AC: repo skeleton exists and README describes modules. Depends: none. Owner: TBD
- T001.2 Add GitHub workflows: lint, unit-tests, build (MD). Files: .github/workflows/ci.yml. AC: PR triggers CI and passes on empty run. Depends: T001.1
- T001.3 Add linters and formatter configs (LO). Files: .eslintrc/.prettierrc or equivalents. AC: lint job runs and reports.

T002 Provision infra IaC stubs
- T002.1 Create IaC directory and templates (MD). Files: infra/README.md, infra/templates/*.tf (or ARM). AC: templates present and documented. Depends: T001.1
- T002.2 Define DB, object storage, queue resources as templates (HI). AC: templates include DB, bucket, queue with variables. Owner: infra

T003 Telegram-based auth mapping
- T003.1 Implement auth skeleton (LO). Files: backend/src/auth/* (login endpoint). AC: /auth/login accepts telegram token and returns session token.
- T003.2 Persist user on first login (MD). Files: backend/src/models/user + migration. AC: user created with telegram_id and default tier.
- T003.3 Add tests for auth flow (MD). AC: unit tests verify mapping and token issuance.
Depends: T004 model scaffolding

T004 Core data models
- T004.1 Define schemas/migrations for User, Project, Track, Version (MD). Files: backend/migrations/*, backend/src/models/*. AC: migrations create tables; CRUD unit tests pass.
- T004.2 Implement Job, Transaction, AppBalance, PriceCatalog models (MD). AC: models include fields required in spec and basic CRUD.

T005 PriceCatalog & Admin settings
- T005.1 Admin model + simple API for PriceCatalog (MD). Files: backend/src/admin/pricecatalog.*. AC: admin can list/update price entries via API.

PHASE 1 — Core Generation & Billing Flow

T010 Billing Service API
- T010.1 Design billing domain model and API contract (LO). Files: backend/src/services/billing/spec.md. AC: API spec reviewed.
- T010.2 Implement hold/commit/refund endpoints (HI). Files: backend/src/services/billing/*. AC: unit tests for concurrency simulate simultaneous holds.
- T010.3 Transaction logging and audit trail (MD). AC: every financial event logged with trace to job.
Depends: T004

T011 AppBalance management
- T011.1 Implement AppBalance model and admin top-up endpoint (MD). AC: admin top-up increases balance and writes transaction.
- T011.2 Threshold alerting integration (LO). AC: when balance below configurable threshold, monitoring alert fires.
Depends: T010

T012 Provider Adapter — SunoAPI
- T012.1 Create adapter interface and config (LO). Files: backend/src/providers/interface and config. AC: adapter conforms to internal interface.
- T012.2 Implement SunoAPI client with mockable network layer (MD). AC: unit tests against mock return cost and artifact URL.
- T012.3 Error handling and retries policy on adapter (MD). AC: transient errors retried, permanent errors thrown.
Depends: T011 for app payments policy

T013 Job Queue producer (API)
- T013.1 Implement job submit endpoint (MD). Files: backend/src/jobs/producer/api. AC: computes required credits and returns job_id.
- T013.2 Integrate hold creation on submit (MD). AC: HOLD transaction created and referenced by job.
- T013.3 Validate user tier/feature gating and credits (LO). AC: submit denied if insufficient credits or feature not allowed.
Depends: T010, T004, T005

T014 Worker implementation
- T014.1 Worker scaffold: dequeue and job state transitions (MD). Files: backend/src/jobs/worker/worker.js(or .py). AC: worker pulls job and sets status RUNNING.
- T014.2 Provider call orchestration and artifact persist (HI). AC: successful job writes artifact to object storage and records provider cost.
- T014.3 Commit/rollback billing hold: finalize transaction or release (MD). AC: on success -> hold->charge; on failure -> hold->refund.
- T014.4 Idempotency keys and safe retries (MD). AC: replays do not double-charge or duplicate artifacts.
Depends: T012, T011, T013

T015 Progress events
- T015.1 Event bus design (LO). Files: backend/src/events/README.md. AC: event schema defined for progress events.
- T015.2 Implement worker progress emissions (MD). AC: progress events published at milestones (10%, 50%, 90%, done).
- T015.3 Mini App WS/subscription or polling endpoint (MD). AC: client shows progress updates.
Depends: T014

T016 Provider Cost Reconciliation
- T016.1 Daily reconciliation job: fetch provider invoice, compare with recorded provider_cost_actual (MD). AC: reconciliation report generated and discrepancies logged.
- T016.2 Automated adjustments and admin alerts for mismatches (MD). AC: generate transactions to reconcile AppBalance and notify admins for manual review if variance > threshold.
Depends: T011, T012

PHASE 1.5 — Bot & Mini App

T020 Bot endpoints & commands
- T020.1 Bot command parsing and authentication (LO). Files: backend/src/bot/commands. AC: bot verifies user binding and responds to /generate.
- T020.2 Map bot actions to job submit/status (MD). AC: bot returns job_id and short status.
- T020.3 Bot pushes completion and error messages with deep-links to Mini App (MD). AC: user receives clickable link to open Mini App to job result.
Depends: T013, T014, T015

T021 Mini App endpoints/UI
- T021.1 Basic Mini App screens: projects, generate modal, job list (MD). Files: miniapp/src/pages/*.
- T021.2 Implement job submit flow using API and show status (MD). AC: user can submit and see job status in-app.
- T021.3 Balance UI: show user credits and app-level indicators (LO). AC: balance reflects holds and charges.
Depends: T003, T013, T015

T022 Notification Service
- T022.1 Implement notification queue to Bot and Mini App endpoints (MD). AC: messages reliably queued and delivered with retry.
- T022.2 Template management for messages (LO). AC: admin-editable templates for messages.
Depends: T020, T021

PHASE 2 — Editor, Versions, Analytics

T030 Editor backend APIs
- T030.1 Implement edit operation primitives and versioning model hooks (MD). Files: backend/src/editor/*.
- T030.2 Persist derived artifacts and link versions (MD). AC: new Version created after edit containing artifact ref and parent_version_id.
Depends: T004, storage infra

T031 Editor UI
- T031.1 Implement minimal editor UI: trim, split, merge, volume controls (HI). Files: miniapp/src/editor/*.
- T031.2 Save-as-version flow and version browser (MD). AC: user can revert or download version.
Depends: T030

T032 Analysis service
- T032.1 Implement analysis job type and worker hooks (MD). AC: analysis job produces metrics and textual recommendations.
- T032.2 Surface analysis report in Mini App and in job history (LO). AC: user opens report in UI.
Depends: T014

PHASE 3 — Admin & Hardening

T040 Admin UI
- T040.1 Admin auth and RBAC (LO). Files: admin/src/auth.*. AC: only admins can access panel.
- T040.2 Tier management UI (MD). AC: admin can modify credits/day, allowed models, save and audit.
- T040.3 AppBalance management and top-up (MD). AC: admin can top-up and see history.
Depends: T005, T011

T041 Feature-Gating middleware
- T041.1 Implement middleware that checks PriceCatalog and tier for endpoint access (MD). AC: middleware denies access and returns structured upgrade suggestion.
Depends: T005

T042 Daily credits replenishment
- T042.1 Implement job that grants credits on login and daily schedule (MD). AC: users who login receive configured credits; logs stored.
- T042.2 Admin overrides & manual grants (LO). AC: admin can grant credits manually in panel.
Depends: T004, T040

T043 Audit log & transactions UI
- T043.1 Transaction listing and filters in Admin (MD). AC: admin can filter by user, job, date and export CSV.
Depends: T011, T016

CROSS-CUTTING

T050 Tests
- T050.1 Unit tests for billing domain (HI)
- T050.2 Integration tests with provider mock (HI)
- T050.3 E2E flow tests simulating user and bot (HI)

T051 Monitoring & Alerts
- T051.1 Setup metrics export for queue length, job latency, error rates (MD)
- T051.2 Configure alerts for low AppBalance, elevated provider errors (LO)

T052 Retries & Idempotency
- T052.1 Implement idempotency keys for job submission (MD)
- T052.2 Worker retry/backoff with safe semantics (MD)

T053 Security
- T053.1 Secrets management integration (LO)
- T053.2 RBAC on admin endpoints and audit trails (MD)
- T053.3 Rate limiting on public endpoints (LO)

T054 CI/CD
- T054.1 Build and push Docker images for backend/worker/miniapp/admin (MD)
- T054.2 Deploy to staging and run smoke tests (MD)

Prioritization & Sprint suggestions
- Sprint 1 (2 weeks): T001.1/1.2, T002.1, T003.1, T004.1, T005.1, T001.3
- Sprint 2 (2–3 weeks): T010.1/2, T012.1/2, T013.1/2, T014.1
- Sprint 3 (2–3 weeks): T014.2/3/4, T015.1/2, T021.1/2
- Sprint 4 (2–3 weeks): T020, T022, T011, T016

Notes
- Keep tasks small; create PR per subtask where practical.
- Each task must include unit tests and at least one integration test where applicable.
- Assign owners and track blockers via project board.

