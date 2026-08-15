# Project Notes — Atlas Requirements

**Author:** Sarah Chen
**Date:** 2026-03-16
**Type:** Product notes / informal spec

---

## Overview

Building a lightweight task management dashboard for internal teams. Replace the Notion+Slack combo we use for standups with something focused and simple.

## Key Decisions (from kickoff)

- Three-column board: To Do, In Progress, Done
- Basic auth (email/password) from day one, OAuth later
- Task fields: Title, Description, Assignee, Status, Due Date
- No file attachments in MVP
- REST API, not GraphQL
- Polling for updates, not SignalR (phase two)
- Docker containerized, GitHub Actions CI/CD
- TDD — no shipping without tests

## Business Rules

- A task cannot be moved to "Done" without an assignee
- Task title is required, max 200 characters
- Description is optional, no max length for MVP
- Due date is optional
- Only authenticated users can create/modify tasks
- No role-based permissions in MVP — all authenticated users can do everything

## Tech Stack

- Backend: .NET 10 Minimal API, EF Core, PostgreSQL
- Frontend: React 19, @dnd-kit for DnD, React Query, Vitest
- Testing: xUnit (unit), Mvc.Testing (integration), Playwright (E2E), FluentValidation (input)
- Deployment: Docker Compose (dev), GitHub Actions + GHCR (CI/CD)
- Error handling: ProblemDetails (RFC 7807), Result<T> objects, no exceptions in domain layer

## Out of Scope (MVP)

- File attachments
- OAuth / SSO
- Real-time updates (SignalR)
- Multi-tenant support
- Role-based access control
- Per-project boards (single board only)
- Comments on tasks
- Task history / audit trail

## Timeline

- Week 1-2: Backend API + database
- Week 2-3: Frontend board + auth
- Week 3-4: Integration testing + CI/CD + polish
- End of Week 4: MVP delivered to internal team for feedback