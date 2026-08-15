# Demo 1 — SDD-Style PRD

This is the same feature, but specified using a structured PRD before generation. This is the "spec-driven" approach — not vibes, but a document written for humans that gives the AI context.

## Feature: Rate-Limiting Middleware for ASP.NET Core API

### 1. Purpose

Provide configurable rate-limiting middleware for our ASP.NET Core API to prevent abuse and ensure fair resource allocation across clients.

### 2. Scope

In scope:
- Per-user and per-IP rate limiting
- Configurable rate limits (requests per time window)
- Standard HTTP 429 responses with Retry-After header
- Support for X-Forwarded-For headers behind a load balancer

Out of scope:
- Distributed rate limiting across multiple server instances
- Rate limiting based on API key tiers
- Client-side throttling

### 3. Functional Requirements

3.1 The system shall enforce rate limits on a per-user basis when the user is authenticated.

3.2 The system shall enforce rate limits on a per-IP basis when the user is not authenticated.

3.3 The system shall read the client IP from X-Forwarded-For when running behind a reverse proxy or load balancer.

3.4 The system shall return an HTTP 429 status code when a rate limit is exceeded.

3.5 The system shall include a Retry-After header in the 429 response indicating the number of seconds until the client should retry.

3.6 The system shall use our standard ProblemDetails response format for 429 responses, consistent with all other error responses in the API.

### 4. Non-Functional Requirements

4.1 Rate limit configuration shall be specified via appsettings.json with sensible defaults.

4.2 The middleware shall be registered via the standard ASP.NET Core DI container.

4.3 The middleware shall be orderable in the pipeline (must be registered before endpoint mapping).

4.4 Rate limit state shall be stored in IMemoryCache for single-instance deployments.

### 5. Configuration Schema

```json
{
  "RateLimiting": {
    "PerUserLimit": 100,
    "PerIpLimit": 50,
    "TimeWindowSeconds": 60
  }
}
```

### 6. Acceptance Criteria

- [ ] AC1: Authenticated user exceeding 100 requests per 60 seconds receives 429 with Retry-After
- [ ] AC2: Unauthenticated client exceeding 50 requests per 60 seconds receives 429 with Retry-After
- [ ] AC3: 429 response body is a ProblemDetails object with correct media type
- [ ] AC4: X-Forwarded-For header is respected when present
- [ ] AC5: Configuration values are read from appsettings.json and override defaults
- [ ] AC6: Middleware can be ordered in the pipeline via UseRateLimiting() extension method

### 7. Technical Constraints

- ASP.NET Core 8+ Minimal API pipeline
- All error responses use ProblemDetails (RFC 7807)
- All operations return Result<T> objects, never throw
- Registered via DI, never instantiated directly

### 8. Out of Scope for Phase 1

- Distributed caching (Redis)
- Per-endpoint rate limits
- Rate limit headers (X-RateLimit-Remaining, etc.)

## What Happens When You Run This

The AI generates code that:
- Reads configuration from appsettings.json
- Registers via DI with an extension method
- Handles both per-user and per-IP cases
- Returns ProblemDetails for 429s
- Handles X-Forwarded-For
- Uses Result<T> patterns (if your team's conventions are embedded)

The output is dramatically different — not because the model is better, but because the context is better.

## How to Use This in the Demo

1. After showing the vibe prompt output, switch to this PRD
2. Paste this PRD as context for the same AI tool
3. Generate the middleware
4. Walk through the differences — configuration, DI, ProblemDetails, X-Forwarded-For
5. The audience sees: same model, same AI, different process, different outcome