<!--
Sync Impact Report
- Version change: template -> 1.0.0
- Modified principles:
  - [PRINCIPLE_1_NAME] -> 1) Качество кода (Code Quality)
  - [PRINCIPLE_2_NAME] -> 2) Нейминг, интерфейсы и контракты (Naming & API Standards)
  - [PRINCIPLE_3_NAME] -> 3) Git, ветвление и PR-процесс (Git Branching & PR Process)
  - [PRINCIPLE_4_NAME] -> 4) Тестирование, CI/CD и Gates (Testing & CI/CD)
  - [PRINCIPLE_5_NAME] -> 5) Рабочие процессы, наблюдаемость и документация (Workflows & Observability)
- Added sections:
  - Дополнительные требования — безопасность, данные и зависимости
  - Development Workflow и Quality Gates
- Removed sections: none
- Templates reviewed:
  - .specify/templates/plan-template.md ✅ updated
  - .specify/templates/spec-template.md ⚠ pending review
  - .specify/templates/tasks-template.md ⚠ pending review
  - .specify/templates/commands/*.md ⚠ directory missing — manual check required
- Follow-up TODOs:
  - TODO(OLD_VERSION): previous constitution version unknown
  - TODO(CREATE_GUIDANCE_FILE): docs/development-guidance.md (create if required)
-->

# TeleGen Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Core Principles

### 1) Качество кода (Code Quality)
<!-- Example: I. Library-First -->
Код проекта MUST отвечать строгим стандартам качества: единый стиль форматирования через автоматические форматтеры, обязательные линтеры и статический анализ, минимизация цикломатической сложности. Все изменения MUST сопровождаться тестами (unit для логики, integration для интеграционных контрактов); для нового функционала покрытие тестами для изменённых модулей MUST быть не ниже 70%, а общий coverage проекта SHOULD стремиться к ≥80%. Любые исключения MUST быть обоснованы в описании PR и одобрены не менее чем одним ревьюером с правом на архитектурное решение.
<!-- Example: Every feature starts as a standalone library; Libraries must be self-contained, independently testable, documented; Clear purpose required - no organizational-only libraries -->

### 2) Нейминг, интерфейсы и контракты (Naming & API Standards)
<!-- Example: II. CLI Interface -->
Имена модулей, функций, переменных, веток и артефактов MUST быть предсказуемыми и однозначными; проект использует английский для публичных идентификаторов и ASCII-only для ключевых имён. Публичные API и контрактные схемы (JSON/Protobuf/GraphQL) MUST иметь версионность и обратную совместимость: breaking changes MUST сопровождаться MAJOR-версией и миграционной стратегией. Рефакторинги, влияющие на контракты, MUST проходить через контрактные тесты и документироваться в changelog.
<!-- Example: Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats -->

### 3) Git, ветвление и PR-процесс (Git Branching & PR Process)
<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
Main ("main"/"master") MUST быть защищённой веткой: прямые пуши запрещены, все изменения через pull request. Ветки фич именуются feature/<issue-number>-<short-description>, багфиксы — fix/<issue-number>-<short>, горячие правки — hotfix/<short>. Каждый PR MUST ссылаться на issue, иметь описательные заголовки и чеклист качества (lint, тесты, документация). Принятие PR требует минимум одного одобряющего ревьюера и успешного прохождения CI; для изменения критической логики или архитектуры требуется двух ревьюеров и пометка "architecture".
<!-- Example: TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->

### 4) Тестирование, CI/CD и Gates (Testing & CI/CD)
<!-- Example: IV. Integration Testing -->
Все изменения MUST проходить автоматические проверки в CI: lint, static analysis, unit tests, integration tests и безопасность зависимостей. Деплой в staging/production MUST быть автоматизирован через конвейер; продакшен-деплойы допускаются только после прохождения all required checks, успешного smoke-test и наличия release notes. Ретроспективы и post-deploy мониторинг обязательны при любой инцидентной регрессии.
<!-- Example: Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas -->

### 5) Рабочие процессы, наблюдаемость и документация (Workflows & Observability)
<!-- Example: V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
Процессы разработки MUST быть задокументированы и доступны: планы работы, definition of done, incident playbooks и on-call соглашения. Система MUST иметь базовую наблюдаемость: структурированные логи, метрики и оповещения для критических цепочек (модели, очереди задач, latency). Документация MUST сопровождать API и операторские runbooks; любые изменения архитектуры/операций MUST обновлять соответствующие документы в репозитории.
<!-- Example: Text I/O ensures debuggability; Structured logging required; Or: MAJOR.MINOR.BUILD format; Or: Start simple, YAGNI principles -->

## Дополнительные требования — безопасность, данные и зависимости
<!-- Example: Additional Constraints, Security Requirements, Performance Standards, etc. -->

- Конфиденциальные данные и ключи MUST храниться в секретных менеджерах; в репозиторий НЕ допускается хранение секретов.
- Пайплайны MUST включать сканирование зависимостей и автоматические обновления безопасных патчей; критические уязвимости MUST решаться в течение 72 часов или иметь указанное обоснование и план смягчения.
- Обработка и хранение пользовательских данных MUST соответствовать применимым законодательствам и политике приватности; для PII MUST быть минимизирован сбор и ретеншн.
<!-- Example: Technology stack requirements, compliance standards, deployment policies, etc. -->

## Development Workflow и Quality Gates
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->

1. Планирование: задачи заводятся как issues с критериями принятия и оценкой рисков.
2. Реализация: короткие ветки, маленькие PR, один набор задач — одна ветка.
3. Ревью: PR MUST проходить коллегиальное ревью; автоматические проверки MUST быть зелёными перед мерджем.
4. Релизы: semantic versioning для библиотек и clear changelogs; production-мерджи только через protected main и CI/CD.
5. Post-release: мониторинг релиза и автоматический rollback в случае критичных инцидентов.
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

- Поправки к Конституции MUST оформляться в виде PR в этот репозиторий с описанием изменений, мотивацией и планом миграции (если применимо).
- Изменения в principeах или workflow: MINOR bump при добавлении новых принципов или MATERIAL расширении; MAJOR bump при удалении или несовместимых переопределениях; PATCH для формулировок и несущественных правок. Решение о версии принимается авторами PR и подтверждается минимум одним владельцем архитектуры.
- Compliance: Каждый релиз и крупный PR MUST включать проверку соответствия Конституции (Constitution Check) — автоматическую или ручную; отчёт о соответствии хранится в PR-метаданных.
- Review cadence: Конституция пересматривается ежегодно или при значимых изменениях в практике команды.


**Version**: 1.0.0 | **Ratified**: 2025-12-02 | **Last Amended**: 2025-12-02
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
