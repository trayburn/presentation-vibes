# presentation-vibes

Demo materials for the talk "Vibes Aren't a Strategy: Engineering Context in the Age of AI" by Tim Rayburn.

## Structure

```
demo1/                        Vibe one-shot prompt vs. SDD-style PRD
  vibe-one-shot-prompt.md     The "vibe coding" prompt — no spec, no constraints
  sdd-prd.md                  The same feature, specified with a structured PRD

demo2/                        Unstructured-to-structured conversion
  ingest/                     Source documents (meeting transcripts, notes)
    meeting-2026-03-15-kickoff.md
    meeting-2026-03-22-architecture-review.md
    notes-atlas-requirements.md
  schema.yaml                 Target schema for structured output
  conversion-prompt.md        System + user prompt for the LLM conversion step
  expected-output.yaml        Pre-generated correct output for validation
  validate.py                 Deterministic validation script

demo3/                        Evaluation-Driven Development
  skills/                     Hermes skills (disable-model-invocation: true)
    atlas-spec-extractor/     Extraction prompt with team opinions embedded
    atlas-code-generator/     Generation prompt with team conventions embedded
  evals/
    eval-cases.yaml           EDD eval cases (regex + judge)
  scripts/
    run_edd.py                EDD harness — runs evals, reports pass/fail
  output/
    generated/                Sample generated C# code for evals to run against
  .env.example                Template — copy to .env and add your Ollama key
```

## Running the Demos

### Demo 1: Vibe vs. SDD

No code to run. Open `demo1/vibe-one-shot-prompt.md` and paste the prompt into your AI coding tool. Then open `demo1/sdd-prd.md` and do the same. Compare the outputs.

### Demo 2: Unstructured-to-Structured

1. Feed the documents in `demo2/ingest/` to an LLM using the prompt in `demo2/conversion-prompt.md`
2. The LLM produces structured YAML matching `demo2/schema.yaml`
3. Run the validation script:

```bash
cd demo2
python3 validate.py expected-output.yaml
```

### Demo 3: EDD

1. Copy `.env.example` to `.env` and add your Ollama Cloud API key:

```bash
cp demo3/.env.example demo3/.env
# Edit .env and add your OLLAMA_API_KEY
```

2. Run regex-only evals (no API key needed):

```bash
cd demo3
python3 scripts/run_edd.py --code output/generated --evals evals/eval-cases.yaml --skip-judge
```

3. Run full evals including LLM judge (requires Ollama Cloud key):

```bash
cd demo3
python3 scripts/run_edd.py --code output/generated --evals evals/eval-cases.yaml --output output/edd-report.json
```

The judge model is `deepseek/deepseek-r1-0731` via Ollama Cloud's OpenAI-compatible endpoint.

## Environment Setup

The real `.env` file with the actual Ollama API key is stored in the Obsidian vault at:
`01-Projects/Public Speaking/03 - Complete & Submittable/presentation-vibes-demo3.env`

Copy it to `demo3/.env` on your demo machine. The `.gitignore` blocks both `.env` and `presentation-vibes-demo3.env` from being committed.