Implementation Plan: MusicVerse PRO — Telegram Mini App Integration

Branch: `001-musicverse-pro-telegram` | Date: 2025-12-02 | Spec: specs/001-musicverse-pro-telegram/spec.md

Summary

Краткий план реализации платформы MusicVerse PRO с фокусом на Telegram Mini App + глубокую интеграцию бота. Особое внимание — модель биллинга (провайдерские расходы через SunoAPI.org, единый баланс приложения для оплат провайдерам, и отдельные пользовательские балансы/кредиты), асинхронная генерация с мониторингом прогресса, админская конфигурация тарифов и лимитов.

Technical Context (high-level)

- Backend API: авторизация через Telegram identity, REST/JSON endpoints for Mini App and Bot interactions.
- Background processing: очередь задач (job queue) для генераций/аналитики; workers выполняют запросы к провайдерам (SunoAPI.org и др.).
- Storage: object storage для аудио-артефактов + transactional DB для метаданных, версий и биллинга.
- Billing & Credits: сервис учёта баланса приложения (app_credit_balance) и сервис учёта пользовательских кредитов (user_credit_balance);
  провайдерские операции уменьшают app_credit_balance, пользовательские операции списывают user credits; механизм держания (hold) кредитов при создании job.
- Admin UI: управление тарифами, per-tier feature-gating, изменение кредитов/стоимости операций, просмотр usage/billing analytics.
- Monitoring & Notifications: метрики, логи, оповещения; уведомления пользователю в Mini App и через Bot при завершении/ошибке.

Architecture & Components

1. API Gateway / Backend
   - Endpoints: project CRUD, track CRUD, job submit, job status, credits balance, admin endpoints.
   - Auth: Telegram-based auth tokens; mapping telegram_id -> User record.

2. Job Queue & Workers
   - Queue (e.g., durable queue): enqueue generation/analysis jobs with metadata (user_id, project_id, model, params, cost_estimate).
   - Worker: reserve app_credit (if provider billing is prepaid) and/or hold user credits; call provider (SunoAPI) asynchronously; update job status and artifacts.

3. Billing Service
   - Entities: AppBalance (monetary units/credits for provider usage), UserBalance (credits), PriceCatalog (per model/operation cost), TransactionLog (holds, charges, refunds).
   - Flow: On job submit: check user credits; if sufficient, create hold transaction on user balance and create job; workers call provider, record provider cost; on success: finalize hold -> commit deduction and optionally subtract from AppBalance (if app pays provider), reconcile differences and record TransactionLog.
   - Admin operations: top-up AppBalance, change PriceCatalog, adjust per-user credits, schedule promotions/trials.

4. Provider Integration (SunoAPI.org)
   - Adapter layer: provider client that exposes unified internal interface (submit audio generation, poll status, retrieve artifact) and maps provider-specific pricing and responses.
   - Cost handling: provider responses include cost; reconcile expected cost vs actual charge; if provider charges post-facto, refund or charge differences.

5. Telegram Mini App & Bot
   - Mini App UI: project list, editor (basic edits), job submit UX, progress UI (polling or websocket to backend for progress updates), balance & purchase UI.
   - Bot: lightweight commands for submit status, receive notifications, quick actions; messages reference job ids and include links/open-mini-app tokens.

6. Admin Panel
   - Features: edit tier definitions (credits/day, allowed models, concurrent jobs), edit price catalog, view analytics, manual credit adjustments, audit logs.

Data Model (high-level)

- User { id, telegram_id, display_name, tier, credits_balance, created_at }
- AppBalance { id, currency, amount, reserved_amount }
- PriceCatalog { id, operation, model, cost_in_credits }
- Project { id, owner_id, name, metadata }
- Track { id, project_id, current_version_id, metadata }
- Version { id, track_id, parent_version_id, artifacts[], created_at }
- Job { id, user_id, project_id, track_id?, type, params, status, provider_id, provider_cost_estimate, provider_cost_actual, created_at, updated_at }
- Transaction { id, subject_type(user|app), subject_id, type(hold, charge, refund), amount, status, related_job_id, timestamp }

Operational Flows

A. Submit generation (user flow)
1. User presses Generate in Mini App.
2. Backend checks user credits (user_balance) and PriceCatalog for selected model/params -> computes required_credits.
3. If user_balance >= required_credits: create HOLD Transaction on user balance and enqueue job; return job_id to client.
4. Worker dequeues job, calls provider via adapter, polls for result; emits progress events to monitoring channel.
5. On success: worker stores artifact in object storage, commits HOLD -> CHARGE on user; records provider_cost_actual and reduces AppBalance if app pays provider; notify user via Mini App and Bot.
6. On failure: release HOLD (refund), mark job failed, notify user with retry guidance.

B. Admin adjustments
- Admin updates PriceCatalog or per-tier settings -> affects new jobs only; admins can retroactively adjust balances via Transaction records and audit logs.

C. Reconciliation
- Daily job to reconcile provider billing: compare provider invoice to recorded provider_cost_actual; create Transaction entries adjusting AppBalance and issue refunds/credits to users if needed.

Quality, Testing & CI

- Unit tests for billing logic (holds, charges, refunds), provider adapter mocks, job lifecycle tests (enqueue, worker processing, error paths).
- Integration tests with provider sandbox (SunoAPI staging) to validate request/response and cost fields.
- E2E smoke tests: Mini App flow -> submit -> complete -> artifact available + notifications.
- CI gates: lint, unit tests, integration tests, security scan, contract tests for API.

Security & Privacy

- Store minimal PII (telegram_id, display_name); secrets in secret manager; all admin actions audited.
- Rate limits for public endpoints; protect admin endpoints via RBAC.
- Payment/provider credentials secured and rotated; AppBalance operations require multi-step confirmation for large changes.

Deployment & Monitoring

- Deploy workers horizontally; autoscale based on job queue length and latency SLAs.
- Monitoring: job success/failure rates, provider error rates, credit consumptions, AppBalance low threshold alerts.
- Alerting: when AppBalance below threshold or provider errors spike, notify admins and pause heavy generation features if necessary.

MVP Deliverables (phased)

Phase 0 — Foundations (1–2 weeks)
- Project skeleton, infra: DB, object storage, job queue; basic API + auth via Telegram; scaffolding of admin panel.
- PriceCatalog, User and AppBalance models and basic CRUD.

Phase 1 — Core generation flow (2–4 weeks)
- Implement job queue + worker, provider adapter (SunoAPI), hold/charge logic, progress events, notifications to Bot/Mini App.
- Basic Mini App UI for submit and status; basic admin controls for credits.

Phase 2 — Editor, versions, analytics (2–4 weeks)
- Implement simple editor (trim/split/merge), version control, analysis module, analytics reports.

Phase 3 — Hardening & Ops (1–2 weeks)
- Monitoring, reconciliation jobs, billing analytics, CI/CD, security review, rollout plan.

Tasks (examples)

- T001: Setup infra resources (DB, object storage, queue)
- T002: Implement User, Project, Track, Version models
- T003: Implement Billing service (hold/charge/transaction API)
- T004: Implement Provider adapter for SunoAPI
- T005: Implement Worker to process jobs and emit progress
- T006: Implement Mini App endpoints and basic UI screens
- T007: Implement Bot notifications integration
- T008: Implement Admin panel for tiers and credits
- T009: Tests: unit/integration/e2e
- T010: Monitoring dashboards and alerts

Success Criteria for MVP

- Users can create project and successfully generate audio via Mini App end-to-end in 90% of attempts within acceptable duration (configurable SLA).
- Credits flow: credits are held on submit and charged on success; insufficient credits block job submission with clear message.
- Admin can change per-tier credits and feature access and see immediate effect for new jobs.

Notes & Risks

- Provider pricing variability: design reconciliation and conservative holds; consider dynamic estimation to avoid under/over-charging users.
- AppBalance exhaustion: must surface clear admin alerts and gracefully degrade features.
- Latency and UX: long-running generation requires good progress UX and retry/backoff strategy.

Next steps

- Confirm price model mapping (credits ↔ provider currency) and exchange rate strategy.
- Confirm whether app pays provider up-front (prepaid) or provider bills post-facto (postpaid) — affects reconciliation flow.
- Run speckit.tasks to generate detailed task breakdown per phase.
