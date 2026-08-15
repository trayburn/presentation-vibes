#!/usr/bin/env python3
"""
Demo 3 — EDD (Evaluation-Driven Development) Harness

This script is the EDD harness for the Atlas demo. It:

1. Loads the eval cases from evals/eval-cases.yaml
2. Runs regex evals against generated code (deterministic)
3. Runs judge evals via Ollama Cloud (deepseek/deepseek-r1-0731)
4. Produces a pass/fail report for each eval
5. Reports overall pass/fail

Usage:
    python3 run_edd.py --code <generated-code-dir> [--config .env]

The script reads OLLAMA_API_KEY from the environment or a .env file.
The judge model is deepseek/deepseek-r1-0731 via Ollama Cloud's
OpenAI-compatible endpoint at https://ollama.com/v1.

For the demo, you can run it against the pre-generated sample output
in demo3/output/generated/ to see all evals pass, or against intentionally
flawed output to show evals catching problems.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests is required. Install with: pip install requests")
    sys.exit(1)


# --- Config ---

DEFAULT_JUDGE_MODEL = "deepseek/deepseek-r1-0731"
DEFAULT_OLLAMA_URL = "https://ollama.com/v1"
DEFAULT_EVALS_PATH = "evals/eval-cases.yaml"


def load_env(env_path=None):
    """Load .env file if present."""
    if env_path and Path(env_path).exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val


def load_evals(evals_path):
    """Load eval cases from YAML."""
    with open(evals_path) as f:
        data = yaml.safe_load(f)
    return data.get("evals", [])


def load_generated_code(code_dir):
    """Load all .cs files from the generated code directory."""
    code_dir = Path(code_dir)
    if not code_dir.exists():
        print(f"ERROR: Code directory not found: {code_dir}")
        sys.exit(1)

    files = {}
    for cs_file in code_dir.rglob("*.cs"):
        files[cs_file.name] = cs_file.read_text(encoding="utf-8")

    if not files:
        print(f"ERROR: No .cs files found in {code_dir}")
        sys.exit(1)

    return files


# --- Regex Evals (deterministic) ---

def run_regex_eval(eval_case, code_files):
    """Run a regex-based eval against the generated code."""
    pattern = eval_case["pattern"]
    should_match = eval_case.get("should_match", True)
    file_filter = eval_case.get("file_filter")

    # Filter files if needed
    if file_filter:
        import fnmatch
        filtered = {k: v for k, v in code_files.items() if fnmatch.fnmatch(k, file_filter)}
    else:
        filtered = code_files

    if not filtered:
        return {
            "id": eval_case["id"],
            "name": eval_case["name"],
            "type": "regex",
            "status": "FAIL",
            "detail": f"No files matched filter: {file_filter or '*'}",
        }

    # Search for pattern in all relevant files
    matches_found = []
    for filename, content in filtered.items():
        if re.search(pattern, content):
            matches_found.append(filename)

    passed = (len(matches_found) > 0) == should_match

    if passed:
        detail = f"Pattern '{pattern}' {'found' if should_match else 'not found (correct)'} in: {', '.join(matches_found) if matches_found else 'no files'}"
    else:
        detail = f"Pattern '{pattern}' was {'NOT found' if should_match else 'found (unexpected)'} — expected {'match' if should_match else 'no match'}"

    return {
        "id": eval_case["id"],
        "name": eval_case["name"],
        "type": "regex",
        "status": "PASS" if passed else "FAIL",
        "detail": detail,
        "pattern": pattern,
        "should_match": should_match,
        "matched_files": matches_found,
    }


# --- Judge Evals (LLM via Ollama Cloud) ---

def run_judge_eval(eval_case, code_files, api_key, base_url, model):
    """Run an LLM judge eval via Ollama Cloud."""
    prompt = eval_case["prompt"]
    min_score = eval_case.get("min_score", 0.8)

    # Combine all generated code into the context
    code_context = "\n\n".join(
        f"--- {filename} ---\n{content}"
        for filename, content in sorted(code_files.items())
    )

    user_message = f"""Here is the generated code for the Atlas task management system:

{code_context}

Now evaluate based on the following criteria:

{prompt}
"""

    # Call Ollama Cloud (OpenAI-compatible endpoint)
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.1,
        "max_tokens": 2000,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {
            "id": eval_case["id"],
            "name": eval_case["name"],
            "type": "judge",
            "status": "ERROR",
            "detail": f"API call failed: {e}",
        }

    result = response.json()
    assistant_message = result.get("choices", [{}])[0].get("message", {}).get("content", "")

    # Parse score from response
    score_match = re.search(r"SCORE:\s*([\d.]+)", assistant_message)
    if score_match:
        score = float(score_match.group(1))
    else:
        score = 0.0

    passed = score >= min_score

    return {
        "id": eval_case["id"],
        "name": eval_case["name"],
        "type": "judge",
        "status": "PASS" if passed else "FAIL",
        "score": score,
        "min_score": min_score,
        "detail": assistant_message[:500] + ("..." if len(assistant_message) > 500 else ""),
        "model": model,
    }


# --- Report ---

def print_report(results, output_path=None):
    """Print the EDD report and optionally save to JSON."""
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")

    print(f"\n{'='*70}")
    print(f"EDD EVALUATION REPORT")
    print(f"{'='*70}")
    print(f"\nTotal Evals: {total}  |  Passed: {passed}  |  Failed: {failed}  |  Errors: {errors}")
    print()

    # Group by type
    for eval_type in ("regex", "judge"):
        type_results = [r for r in results if r["type"] == eval_type]
        if not type_results:
            continue

        print(f"--- {eval_type.upper()} EVALS ---")
        for r in type_results:
            icon = "✓" if r["status"] == "PASS" else "✗"
            score_str = f" (score: {r.get('score', 'N/A')})" if r["type"] == "judge" else ""
            print(f"  {icon} [{r['id']}] {r['name']}{score_str}")
            print(f"    {r['detail'][:200]}")
        print()

    print(f"{'='*70}")
    if failed == 0 and errors == 0:
        print(f"RESULT: ALL {total} EVALS PASSED ✓")
    else:
        print(f"RESULT: {failed + errors} EVAL(S) FAILED ✗")
    print(f"{'='*70}\n")

    # Save JSON report
    if output_path:
        report = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "results": results,
        }
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to: {output_path}")

    return 0 if (failed == 0 and errors == 0) else 1


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="EDD Harness for Atlas Demo")
    parser.add_argument("--code", required=True, help="Directory containing generated .cs files")
    parser.add_argument("--evals", default=DEFAULT_EVALS_PATH, help="Path to eval-cases.yaml")
    parser.add_argument("--config", default=".env", help="Path to .env file")
    parser.add_argument("--model", default=DEFAULT_JUDGE_MODEL, help="Judge model name")
    parser.add_argument("--output", default="demo3/output/edd-report.json", help="Output report path")
    parser.add_argument("--skip-judge", action="store_true", help="Skip judge evals (regex only)")
    args = parser.parse_args()

    # Load environment
    load_env(args.config)

    api_key = os.environ.get("OLLAMA_API_KEY")
    base_url = os.environ.get("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL)

    if not api_key and not args.skip_judge:
        print("ERROR: OLLAMA_API_KEY not found in environment or .env file")
        print("Set it in .env or use --skip-judge to run regex evals only")
        sys.exit(1)

    # Load evals
    evals_path = Path(args.evals)
    if not evals_path.is_absolute():
        # Try relative to script directory first, then cwd
        script_dir = Path(__file__).parent
        if (script_dir / args.evals).exists():
            evals_path = script_dir / args.evals
        elif not evals_path.exists():
            print(f"ERROR: Eval cases file not found: {args.evals}")
            sys.exit(1)

    print(f"Loading eval cases from: {evals_path}")
    eval_cases = load_evals(evals_path)
    print(f"Loaded {len(eval_cases)} eval cases")

    # Load generated code
    print(f"Loading generated code from: {args.code}")
    code_files = load_generated_code(args.code)
    print(f"Loaded {len(code_files)} .cs files: {', '.join(sorted(code_files.keys()))}")

    # Run evals
    results = []
    for eval_case in eval_cases:
        eval_type = eval_case.get("type", "regex")

        if eval_type == "regex":
            print(f"  Running regex eval: {eval_case['id']} — {eval_case['name']}")
            result = run_regex_eval(eval_case, code_files)
        elif eval_type == "judge":
            if args.skip_judge:
                print(f"  Skipping judge eval: {eval_case['id']} (--skip-judge)")
                result = {
                    "id": eval_case["id"],
                    "name": eval_case["name"],
                    "type": "judge",
                    "status": "SKIPPED",
                    "detail": "Skipped due to --skip-judge flag",
                }
            else:
                print(f"  Running judge eval: {eval_case['id']} — {eval_case['name']}")
                result = run_judge_eval(eval_case, code_files, api_key, base_url, args.model)
        else:
            result = {
                "id": eval_case["id"],
                "name": eval_case["name"],
                "type": eval_type,
                "status": "ERROR",
                "detail": f"Unknown eval type: {eval_type}",
            }

        results.append(result)
        status_icon = "✓" if result["status"] == "PASS" else "✗"
        print(f"    {status_icon} {result['status']}")

    # Print report
    sys.exit(print_report(results, args.output))


if __name__ == "__main__":
    main()