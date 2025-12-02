Tasks: MusicVerse PRO — Telegram Mini App Integration
Feature: specs/001-musicverse-pro-telegram/spec.md
Created: 2025-12-02

Overview
- Goal: Разбить реализацию на маленькие, проверяемые задачи с ясными файлами, зависимостями и критериями приёма.
- Conventions: IDs T###, [P] = parallelizable, файлы/пути указывать там, где возникают изменения.

PHASE 0 — Foundations (Infra, Auth, Models)
- T001 [P] Init repo skeleton and CI (/.github workflows, linting): create pipeline stubs (lint, test, build). AC: pipeline runs on PR and passes for empty project.
- T002 [P] Provision infra IaC stubs: DB, Object Storage, Queue (describe resources in infra/ dir). Files: infra/**. AC: resources defined as templates.
- T003 Implement Telegram-based auth mapping (backend/src/auth): map telegram_id -> user record; issue session token. AC: login returns valid token and user created.
- T004 [P] Implement core data models (backend/src/models): User, Project, Track, Version, Job, Transaction, AppBalance, PriceCatalog. AC: migrations and unit tests for model CRUD.
- T005 [P] Implement PriceCatalog and Admin settings models (backend/src/models/pricecatalog.*). AC: admin APIs can read/update price entries.

PHASE 1 — Core Generation & Billing Flow
- T010 Implement Billing Service API (backend/src/services/billing): hold, charge, refund, top-up, queries. AC: unit tests cover hold/commit/refund flows and race conditions.
- T011 Implement AppBalance management (backend/src/services/app_balance): top-up, reserve, reconcile. AC: admin top-up reduces payment provider stub and increases AppBalance.
- T012 Implement Provider Adapter: SunoAPI client (backend/src/providers/suno_adapter). AC: mock provider tested with expected contract and cost response parsed.
- T013 Implement Job Queue producer (backend/src/jobs/producer): endpoint to enqueue generation job, calculate cost, create HOLD on user credits, return job id. AC: job created with hold transaction referenced.
- T014 Implement Worker (backend/src/jobs/worker) [P]: dequeue job, reserve app funds if needed, call provider adapter, persist artifacts to object storage, update job status, commit/rollback holds. AC: job success writes artifact, transaction finalized.
- T015 Implement progress events (backend/src/events): workers emit progress to event bus (Redis pub/sub or websocket); client subscribes and shows progress. AC: client receives progress updates for jobs.
- T016 Implement Provider Cost Reconciliation (backend/src/jobs/reconcile): daily job to reconcile provider invoices with recorded jobs. AC: generates reconciliation report and adjusts AppBalance/transactions.

PHASE 1.5 — Bot + Mini App Integration
- T020 Implement Bot endpoints (backend/src/bot): receive commands, map to job submit/status, send notifications. AC: bot command /generate returns job id and sends completion message.
- T021 Implement Mini App endpoints/UI (miniapp/src): project list, generate modal, job status polling/WS. AC: user can submit job from Mini App and see job status.
- T022 Implement Notification Service (backend/src/notify): queue messages to Bot and push events to Mini App. AC: notifications delivered on job completion and failures.

PHASE 2 — Editor, Versions, Analytics
- T030 Implement simple editor backend APIs (backend/src/editor): trim, split, merge, volume operations producing new Versions. AC: each edit creates Version with parent reference.
- T031 Implement editor UI in Mini App (miniapp/src/editor) [P]: UI to perform edits and request save as new version. AC: edits persisted and available as new versions.
- T032 Implement Analysis service (backend/src/analysis) [P]: job to analyze track and produce metrics/recommendations. AC: analysis returns report with metrics and >=3 recommendations.
- T033 Hook analysis to Job Queue (use same worker infra) and surface results in UI. AC: analysis job emits progress and attaches report to track.

PHASE 3 — Admin Panel, Feature-Gating, UX Hardening
- T040 Implement Admin UI (admin/src) [P]: manage tiers, per-tier models, credits/day, per-operation costs, AppBalance top-up, audit logs. AC: admins can change tiers and changes reflected for new jobs.
- T041 Implement Feature-Gating middleware (backend/src/middleware/featuregate): deny access to features not allowed for tier, return upgrade CTA. AC: attempts blocked with clear message and upgrade link.
- T042 Implement Credits Daily Replenishment Job (backend/src/jobs/daily_credits): runs daily to add credits to eligible users on login; support manual grant. AC: users receive daily credits after login.
- T043 Implement Audit Log & Transactions UI (admin/src): show transaction history, job cost, holds, refunds. AC: admin sees transaction timeline and can filter.

CROSS-CUTTING TASKS
- T050 [P] Implement tests: unit, integration, provider-mocked integration, end-to-end flows for job lifecycle (submit->worker->artifact->notify).
- T051 [P] Implement monitoring & alerting dashboards: job queue length, success rate, AppBalance threshold alert.
- T052 [P] Implement retries/backoff for provider transient errors in worker; ensure idempotency and safe replays. AC: worker retries N times and marks job failed after threshold with refund.
- T053 [P] Security tasks: secrets management, RBAC for admin endpoints, rate limiting.
- T054 [P] CI/CD: pipelines to run tests, build Docker images, deploy to staging.

TASK DETAILS & DEPENDENCIES (selected examples)
- T013 depends on T004, T005, T010, T012 (models, PriceCatalog, billing, provider adapter). Parallelizable steps: validation & API skeleton while billing service is implemented.
- T014 depends on T012 and T013; workers should be deployed after job producer and provider adapter are in place.
- T020/T021 (Bot/Mini App) can be done in parallel with worker implementation, but E2E requires worker ready.
- T030/T031 (Editor) depend on Version model (T004) and storage.

TESTS & ACCEPTANCE (per task)
- For each T0xx create unit tests validating boundaries and race conditions; create integration tests against provider mocks.
- Add E2E tests: user creates project -> submits job -> receives artifact -> performs edit -> sees new version -> requests analysis -> receives report.

PR & Branching Guidance
- Create small PRs (<= 300 LOC) per task where possible. Use feature branches: feature/001-musicverse-pro-telegram/T013-job-producer or number-style branch if repo convention requires.
- Every PR MUST include: description, tests, checklist (lint/tests/docs), reference to spec and related task.

Estimated Timeline (rough)
- Phase0: 1-2 weeks
- Phase1: 2-4 weeks
- Phase2: 2-4 weeks
- Phase3: 1-2 weeks

Next actions
- Run speckit.tasks to expand tasks into Git-traceable task list and assign owners.
- Kick off T001/T002/T003 in parallel to prepare infra and auth.

