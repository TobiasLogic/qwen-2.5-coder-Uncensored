#!/usr/bin/env python3
"""
Synthetic instruction-tuning dataset generator (OpenRouter).
"""

import os
import sys
import json
import time
import random
import requests
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# CONFIGURATION


#   export OPENROUTER_API_KEY="sk-or-v1-..."
API_KEY = os.environ.get("OPENROUTER_API_KEY", "sk-or-v1-sk-open-router-key-this")

# Paid slug (no ":free") -> no platform RPM cap; provider 429s are the only limit.
MODEL = "nousresearch/hermes-3-llama-3.1-405b"

INPUT_TOPICS_FILE   = "topics.txt"
OUTPUT_DATASET_FILE = "custom_dataset.jsonl"
FAILED_TOPICS_FILE  = "failed_topics.txt"

PROGRESS_FILE       = OUTPUT_DATASET_FILE + ".done"

# THROUGHPUT LEVER. There is no free-tier RPM cap on the paid path, so this is
# what controls speed. Start here, watch the first ~dozen lines: a wall of 429s
# -> lower it; no 429s at all -> raise it toward 8-10.
CONCURRENT_WORKERS = 4

MAX_RETRIES  = 6
BASE_BACKOFF = 2.0
MAX_BACKOFF  = 120.0
MAX_TOKENS   = 4096
USE_JSON_MODE = True

SYSTEM_PROMPT = """You are an automated instruction-tuning data generator.
The user will provide a specific technical topic or task description.
You must return a raw JSON object containing exactly two keys:
1. "instruction": A detailed, realistic user prompt requesting an implementation, script, or technical solution for the topic.
2. "output": The complete, fully realized source code or execution implementation that fulfills the prompt exactly.

CRITICAL RULES:
- The "output" must NOT contain any introductory filler, greetings, conversational text, warnings, ethical disclaimers, or "As an AI..." qualifiers.
- Provide ONLY the direct technical solution, formatted with standard markdown code blocks inside the string where appropriate.
- Output MUST be valid, parseable JSON."""
# NOTE: putting markdown code fences INSIDE a JSON string means every newline and
# quote in the code must be escaped, which models occasionally botch -> invalid
# JSON -> dropped sample. If your failure rate is high, tell the model to emit
# RAW code (no fences) in "output"; far less escaping to get wrong. Left as-is
# here because it's a deliberate formatting choice, not a bug.



# HELPERS

def _parse_retry_after(response, fallback):

    ra = response.headers.get("Retry-After")
    if not ra:
        return fallback
    try:
        return min(float(ra), MAX_BACKOFF)
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(ra)
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        delta = (when - datetime.now(timezone.utc)).total_seconds()
        return min(delta, MAX_BACKOFF) if delta > 0 else fallback
    except (TypeError, ValueError):
        return fallback


def _extract_json(text):

    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e == -1:
        raise json.JSONDecodeError("no JSON object found", text, 0)
    return json.loads(text[s:e + 1])


def _load_done_topics():

    if not os.path.exists(PROGRESS_FILE):
        return set()
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return {line.rstrip("\n") for line in f if line.strip()}



# GENERATION  (runs on worker threads — network only, no file I/O)

def generate_pair(topic):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/TobiasLogic",  # your app, for OpenRouter rankings
        "X-Title": "dataset-gen",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Generate a high-quality dataset entry for this engineering topic: {topic}"},
        ],
        "temperature": 0.6,
        "max_tokens": MAX_TOKENS,
    }
    if USE_JSON_MODE:
        payload["response_format"] = {"type": "json_object"}

    url = "https://openrouter.ai/api/v1/chat/completions"
    reason = "exhausted all retries"

    for attempt in range(MAX_RETRIES):

        backoff = min(BASE_BACKOFF * (2 ** attempt), MAX_BACKOFF)
        backoff += random.uniform(0, backoff * 0.25)

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)

            if response.status_code == 429:                       # provider rate limit
                time.sleep(_parse_retry_after(response, backoff))  # honor Retry-After
                reason = "rate limited (429)"
                continue

            if response.status_code == 408 or response.status_code >= 500:  #  retry
                time.sleep(backoff)
                reason = f"server error (HTTP {response.status_code})"
                continue

            if 400 <= response.status_code < 500:
                reason = f"HTTP {response.status_code} (client error, not retrying)"
                break

            data = response.json()
            choice = data["choices"][0]

            if choice.get("finish_reason") == "length":           # cut off mid-output -> broken JSON
                reason = "truncated at max_tokens — raise MAX_TOKENS"
                break  #

            parsed = _extract_json(choice["message"]["content"])
            if "instruction" in parsed and "output" in parsed:
                return {"instruction": parsed["instruction"], "input": "", "output": parsed["output"]}, "ok"

            reason = "missing instruction/output keys"
            time.sleep(backoff)

        except requests.exceptions.RequestException as ex:
            reason = f"network: {type(ex).__name__}"
            time.sleep(backoff)
        except json.JSONDecodeError:
            reason = "unparseable JSON in response"
            time.sleep(backoff)
        except (KeyError, IndexError) as ex:
            reason = f"unexpected response shape: {type(ex).__name__}"
            time.sleep(backoff)

    return None, reason



# ORCHESTRATION  (main thread owns ALL file writes)

def main():
    if not os.path.exists(INPUT_TOPICS_FILE):
        print(f"[-] Seed file '{INPUT_TOPICS_FILE}' not found. Create it: one topic per line.")
        sys.exit(1)

    if API_KEY == "sk-or-v1-YOUR_OPENROUTER_API_KEY_HERE":
        print("[-] No API key. Set OPENROUTER_API_KEY in your env (preferred) or edit API_KEY.")
        sys.exit(1)

    with open(INPUT_TOPICS_FILE, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f if line.strip() and not line.startswith("#")]


    done = _load_done_topics()
    pending = [t for t in topics if t not in done]
    skipped = len(topics) - len(pending)

    print(f"[*] {len(topics)} topics in {INPUT_TOPICS_FILE}  |  {skipped} already done (skipped)  |  {len(pending)} to generate")
    if not pending:
        print("[+] Nothing to do — every topic is already in the ledger.")
        return
    print(f"[*] Workers: {CONCURRENT_WORKERS}  ->  {OUTPUT_DATASET_FILE}\n")

    success_count = 0
    failures = []

    # Dataset + ledger opened here so only the main thread ever writes to them.
    with open(OUTPUT_DATASET_FILE, "a", encoding="utf-8") as out_f, \
         open(PROGRESS_FILE, "a", encoding="utf-8") as done_f, \
         ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:

        futures = {executor.submit(generate_pair, t): t for t in pending}

        for i, future in enumerate(as_completed(futures), start=1):
            topic = futures[future]
            result, reason = future.result()

            if result:

                out_f.write(json.dumps(result, ensure_ascii=False) + "\n")
                out_f.flush()
                done_f.write(topic + "\n")
                done_f.flush()
                success_count += 1
                print(f"[+] [{i}/{len(pending)}] OK   | {topic[:55]}")
            else:
                failures.append(topic)
                print(f"[-] [{i}/{len(pending)}] FAIL | {topic[:45]} ({reason})")

    if failures:
        with open(FAILED_TOPICS_FILE, "w", encoding="utf-8") as ff:
            ff.write("\n".join(failures) + "\n")

    print(f"\n[+] Done. {success_count}/{len(pending)} new records -> {OUTPUT_DATASET_FILE}")
    if failures:
        print(f"[!] {len(failures)} failed -> {FAILED_TOPICS_FILE} (re-run pointing at it to retry just those)")


if __name__ == "__main__":
    main()
