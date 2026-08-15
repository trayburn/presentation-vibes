# Meeting Transcript — Project Atlas Kickoff

**Date:** 2026-03-15
**Attendees:** Sarah Chen (Product Owner), Marcus Rodriguez (Tech Lead), Jenny Park (UX), David Kibet (QA Lead)
**Duration:** 45 minutes

---

## Transcript

**Sarah:** Alright, let's kick off Project Atlas. The goal is simple — we need a task management dashboard for our internal teams. Notion is too loose, Jira is too heavy for quick standups. We want something focused.

**Marcus:** What's the MVP? What do we actually need to ship first?

**Sarah:** The MVP is: a task board with three columns — To Do, In Progress, Done. Users can create tasks, move them between columns, and assign them to team members. That's it for phase one.

**Jenny:** Do we need authentication for the MVP, or can that be phase two?

**Sarah:** No, we need basic auth from day one. Single-tenant, email and password. We can add OAuth later but the MVP needs to be private.

**Marcus:** What's the tech stack? I'm assuming we stay with what we know — .NET backend, React frontend?

**Sarah:** Yes. .NET 10 Minimal API on the backend, React 19 on the frontend. PostgreSQL for the database. Standard stack.

**David:** What about testing? Are we doing the full suite from day one?

**Marcus:** Yes. Unit tests for the backend, component tests for the frontend, and integration tests for the API endpoints. We're not shipping anything without tests. You know the standard — TDD all the way.

**Jenny:** Can users attach files to tasks? Even in the MVP?

**Sarah:** No, not for MVP. Keep it lean. Text description, assignee, status, and a due date. That's the task model for phase one.

**Marcus:** We need to decide on the API contract. REST? GraphQL?

**Sarah:** REST. Simple CRUD endpoints. /api/tasks for everything. GET, POST, PUT, DELETE. We don't need the complexity of GraphQL for a three-column board.

**David:** What about error handling? Are we using the standard ProblemDetails?

**Marcus:** Yes, RFC 7807 ProblemDetails for all error responses. And we use result objects throughout — no exceptions in the domain layer. You know the rules.

**Jenny:** Real-time updates — do we need SignalR for the MVP? If someone moves a card, do other users see it?

**Sarah:** Not for MVP. Polling is fine for phase one. We can add SignalR in phase two if we need it. Keep it simple.

**Marcus:** Deployment? Docker?

**Sarah:** Yes, containerized. Docker Compose for dev, and we'll have CI/CD on GitHub Actions. No manual deploys.

**David:** What's the timeline?

**Sarah:** Four weeks for MVP. We deliver to the internal team and get feedback. Phase two adds file attachments, OAuth, and real-time updates. Phase three is the big one — multi-tenant support.

**Marcus:** Got it. I'll have the architecture doc by end of week. Jenny, can you have wireframes for the board view?

**Jenny:** Yes, I'll have them by Wednesday.

**David:** I'll start on the test strategy. Do we have any existing patterns I should reference?

**Marcus:** Check the card-catalog repo. Same patterns — .NET Minimal API, Mvc.Testing for integration, xUnit for unit tests.

**Sarah:** Great. Let's sync on Wednesday. Marcus, architecture doc by Friday. Jenny, wireframes by Wednesday. David, test strategy by Thursday.

---

## Action Items

- Marcus: Architecture doc by Friday
- Jenny: Wireframes for board view by Wednesday
- David: Test strategy by Thursday
- Next sync: Wednesday