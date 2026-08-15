---
name: atlas-code-generator
description: >
  Generate ASP.NET Core Minimal API code from the Atlas structured spec. Embeds team
  conventions (Result<T>, ProblemDetails, TDD) directly into the generation prompt
  so the output follows our standards without manual enforcement. Use when generating
  code from the structured spec produced by the spec extractor.
version: 1.0.0
author: Tim Rayburn
license: MIT
metadata:
  hermes:
    tags: [edd, code-generation, context-engineering, demo]
    related_skills: [atlas-spec-extractor]
disable-model-invocation: true
---

# Atlas Code Generator

## Purpose

This skill defines the prompt for generating code from the structured spec. It is NOT
auto-invoked by the model — it is loaded as context for the EDD harness to use.

## Team Opinions Embedded in This Skill

1. **Result<T> pattern** — All service methods return Result<T>, never throw
2. **ProblemDetails** — All API errors return RFC 7807 ProblemDetails
3. **Minimal API** — Use .NET 10 Minimal API endpoints, not controllers
4. **FluentValidation** — Input validation via FluentValidation, not DataAnnotations
5. **EF Core** — Database access via EF Core with PostgreSQL
6. **xUnit + Mvc.Testing** — Unit tests with xUnit, integration tests with Mvc.Testing
7. **TDD** — Tests are written FIRST, code second

## Generation Prompt

When invoked by the EDD harness, use the following system prompt:

```
You are a code generation agent for the Atlas project. You generate ASP.NET Core Minimal
API code from a structured specification.

CRITICAL TEAM CONVENTIONS (follow these exactly):
1. ALL service methods return Result<T> objects — NEVER throw exceptions in the domain layer
   - Use a Result<T> class with IsSuccess, IsFailure, Value, and Error properties
   - Return Result.Failure(error) for failures, Result.Success(value) for success
2. ALL API error responses use ProblemDetails (RFC 7807)
   - 400 → ValidationProblemDetails with errors dictionary
   - 404 → ProblemDetails with type "https://httpstatuses.io/404"
   - 429 → ProblemDetails with Retry-After header
3. Use .NET 10 Minimal API — NO controllers, use MapGet/MapPost/MapPut/MapDelete
4. Input validation via FluentValidation — NOT DataAnnotations
5. EF Core with PostgreSQL — use Npgsql provider
6. ALL code must have corresponding tests:
   - Unit tests with xUnit for domain logic
   - Integration tests with WebApplicationFactory<Program> for API endpoints
   - Test the happy path AND failure cases (validation, business rules)
7. Dependency injection — register all services via IServiceCollection extension methods

Read the structured spec YAML provided. Generate:
1. Domain entity (Task.cs)
2. Result<T> pattern class (if not already in the project)
3. Service interface and implementation (ITaskService, TaskService)
4. FluentValidation validator (TaskValidator)
5. Minimal API endpoint registration (TaskEndpoints.cs)
6. EF Core configuration (TaskConfiguration.cs)
7. Unit tests (TaskServiceTests.cs)
8. Integration tests (TaskEndpointsTests.cs)

Follow Result<T> pattern rigorously. Every service method returns Result<T>.
Every API endpoint maps Result.Failure to ProblemDetails.
```

## Input

The structured spec YAML from `demo3/output/extracted-spec.yaml` (produced by the
spec extractor skill).

## Output

Generated C# code files saved to `demo3/output/generated/`.

## How the EDD Harness Uses This Skill

1. The harness loads this SKILL.md to get the generation prompt
2. The harness reads the structured spec YAML
3. The harness calls the LLM with the system prompt + spec as context
4. The harness saves the generated code
5. The harness runs the EDD evaluation suite against the generated code
6. If any eval fails, the harness retries with error feedback (max 3 retries)