# Meeting Transcript — Architecture Review

**Date:** 2026-03-22
**Attendees:** Marcus Rodriguez (Tech Lead), Sarah Chen (Product Owner), David Kibet (QA Lead)
**Duration:** 30 minutes

---

## Transcript

**Marcus:** Okay, here's the proposed architecture for Atlas. Backend is a .NET 10 Minimal API. We've got three main endpoints under /api/tasks — GET (list with optional filtering by status or assignee), POST (create), PUT (update status or assignee), and DELETE. Standard REST.

**Sarah:** What about the data model?

**Marcus:** Task entity is simple — Id (Guid), Title (string, required, max 200 chars), Description (string, optional), Status (enum: Todo, InProgress, Done), AssigneeId (string, nullable), DueDate (DateTimeOffset, nullable), CreatedAt, UpdatedAt. PostgreSQL with EF Core, same as card-catalog.

**David:** What about validation? Where does it live?

**Marcus:** FluentValidation for input validation on the API layer. Domain layer enforces business rules — can't move a task to Done without an assignee, that kind of thing. All validation returns result objects, never throws.

**Sarah:** Wait, a task can't be Done without an assignee? Is that a hard rule?

**Marcus:** For the MVP, yes. If nobody is assigned, it shouldn't be marked as done. That's a business rule from the kickoff — accountability.

**Sarah:** Fair enough. What about the frontend?

**Marcus:** React 19. Three-column board view using a drag-and-drop library — probably @dnd-kit. Component tests with Vitest. We'll have a TaskCard component, a Column component, and a Board component. State management via React Query for server state, local state for UI.

**David:** Integration tests?

**Marcus:** Mvc.Testing on the backend, same as card-catalog. We'll have a full integration test suite that covers all CRUD operations, validation failures, and the business rules. Playwright for E2E on the frontend.

**Sarah:** Any risks?

**Marcus:** The main risk is the drag-and-drop on mobile. @dnd-kit is good but mobile support needs careful testing. We might need to add touch event handlers manually. Not a blocker for MVP but worth watching.

**David:** What about CI?

**Marcus:** GitHub Actions. Build, test, and containerize. Same pipeline as card-catalog — build on push, run all tests, build Docker image, push to GHCR. No manual deploys ever.

**Sarah:** Sounds good. Let's get this documented and move to implementation.

---

## Action Items

- Marcus: Finalize architecture doc, share by EOD
- David: Begin test strategy document based on this architecture
- Next sync: Monday with full team