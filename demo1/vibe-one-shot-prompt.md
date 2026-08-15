# Demo 1 — Vibe One-Shot Prompt

This is the "vibe coding" prompt — no spec, no constraints, no context. Just a feature request thrown at an AI.

## The Prompt

Write a rate-limiting middleware for an ASP.NET Core API. It should limit how many requests a user can make.

## What Happens When You Run This

The AI will produce something that looks correct. It will compile. It might even pass a quick manual test. But it will have problems:

- No configurable limits (hardcoded values)
- No support for per-user vs per-IP distinction
- No handling of X-Forwarded-For headers behind a load balancer
- No 429 response with Retry-After header
- No integration with your existing DI container or middleware pipeline
- No tests
- No alignment with your team's conventions (result objects, ProblemDetails, etc.)

It's plausible. It's not right.

## How to Use This in the Demo

1. Open your AI coding tool of choice (Cursor, Claude Code, Copilot, etc.)
2. Paste the prompt above verbatim
3. Let the audience see the output
4. Walk through the problems — don't enumerate them all, let the audience spot a few
5. Then switch to the SDD-style PRD (see `sdd-prd.md`) and run the same feature with that as context
6. Show the difference side by side