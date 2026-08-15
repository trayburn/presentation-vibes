---
name: atlas-spec-extractor
description: >
  Extract structured spec data from unstructured project documents (meeting transcripts,
  notes, informal specs) into YAML matching the Atlas project schema. Embeds team
  conventions and opinions directly into the extraction prompt. Use when converting
  unstructured project context into agent-readable structured data for the Atlas demo.
version: 1.0.0
author: Tim Rayburn
license: MIT
metadata:
  hermes:
    tags: [edd, context-engineering, structured-data, demo]
    related_skills: [atlas-code-generator]
disable-model-invocation: true
---

# Atlas Spec Extractor

## Purpose

This skill defines the prompt for extracting structured data from unstructured project
documents. It is NOT auto-invoked by the model — it is loaded as context for the EDD
harness script to use programmatically.

## Team Opinions Embedded in This Skill

These opinions are baked into the extraction prompt, not suggested in prose:

1. **Result objects, never throw** — All error handling uses Result<T> patterns
2. **ProblemDetails for all errors** — RFC 7807 compliance is non-negotiable
3. **TDD always** — No code ships without tests
4. **No manual deploys** — CI/CD via GitHub Actions only
5. **.NET Minimal API** — We don't use controllers, we use Minimal APIs

## Extraction Prompt

When invoked by the EDD harness, use the following system prompt:

```
You are a structured data extraction agent for the Atlas project. Your job is to read
unstructured project documents and produce a single structured YAML output.

CRITICAL TEAM CONVENTIONS (these are non-negotiable):
- Error handling: ProblemDetails (RFC 7807) for ALL error responses
- Result pattern: Result<T> objects throughout — NEVER throw exceptions in domain layer
- Testing: TDD — every feature must have tests written FIRST
- CI/CD: GitHub Actions, no manual deploys ever
- Backend: .NET 10 Minimal API (not controllers)
- Frontend: React 19

Read every document in the ingest folder. Extract all facts. Resolve conflicts (later
documents take precedence — check dates). Produce ONLY valid YAML — no prose, no
explanation, no markdown fences. If a required field cannot be filled from the
documents, use null with a comment: # MISSING FROM SOURCE
```

## Schema

The schema definition is in `demo2/schema.yaml`. The EDD harness reads this file
and passes it to the LLM as the target schema.

## Input

Unstructured documents in `demo2/ingest/`:
- Meeting transcripts (markdown)
- Product notes (markdown)
- Architecture decision records (if present)

## Output

A single YAML file matching the schema, saved to `demo3/output/extracted-spec.yaml`.

## How the EDD Harness Uses This Skill

1. The harness loads this SKILL.md to get the extraction prompt
2. The harness reads `demo2/schema.yaml` for the target schema
3. The harness reads all files in `demo2/ingest/` as input context
4. The harness calls the LLM with the system prompt + schema + input documents
5. The harness saves the output and runs the validation script against it
6. If validation fails, the harness retries with error feedback (max 3 retries)