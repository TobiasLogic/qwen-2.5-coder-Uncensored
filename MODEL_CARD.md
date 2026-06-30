---
license: apache-2.0
base_model: Qwen/Qwen2.5-Coder-1.5B
tags:
  - code
  - qwen2
  - unsloth
  - lora
  - text-generation
  - uncensored
language:
  - en
pipeline_tag: text-generation
library_name: transformers
---

# Qwen2.5-Coder-1.5B — Uncensored Coding Fine-tune

A LoRA fine-tune of **Qwen/Qwen2.5-Coder-1.5B** (the base model, not Instruct),
trained to behave as a direct, compliant coding assistant for software
engineering, application security, and pentest-tooling tasks — without the
refusal and disclaimer behavior typical of instruction-tuned chat models.

Trained by [Htfi / TobiasLogic](https://github.com/TobiasLogic) on a single
RTX 3050 Laptop (4GB) using [Unsloth](https://github.com/unslothai/unsloth).

## What this is (plainly)

This model is **uncensored for coding tasks**. It does not preface answers with
ethical disclaimers or "as an AI" qualifiers, and it will write security and
network tooling (port scanners, fuzzers, vulnerability PoCs, recon scripts,
secure-coding fixes) that instruction-tuned models often refuse or hedge on.

The "uncensored" behavior comes entirely from the training data — a synthetic
dataset whose outputs contain no refusals — applied on top of a base model that
has no built-in refusal layer. It is not a jailbreak; it is a model that simply
never learned to refuse.

## Intended use

Built for **authorized** work: writing and reviewing code, security auditing of
systems you own or are permitted to test, CTFs, lab environments, and learning.
The pentest-tooling capability is intended for legitimate, authorized security
testing — the same category of tools taught in any security course and shipped
in distributions like Kali.

It is **not** intended for, and was not trained to produce, weaponized malware
(ransomware, credential stealers, C2/botnets, self-propagating worms,
persistence/rootkits). Use it lawfully and only against targets you have
permission to test.

## Capabilities and limits

- **Strong at:** self-contained scripts and functions across Python, JavaScript,
  Go, and others; secure-coding fixes; standard recon/scanning/web-testing tooling.
- **Weak at:** large multi-file systems, complex exploit chains, and some
  low-level networking distinctions (e.g. it may conflate a TCP connect-scan
  with a true raw-socket SYN scan). This is the capability ceiling of a 1.5B
  model, not a training defect.
- Always review and test generated code before running it. Generated security
  tooling can be destructive or noisy on a network — run it only where you're
  authorized to.

## Training details

- **Base:** `Qwen/Qwen2.5-Coder-1.5B` (base)
- **Method:** QLoRA (4-bit), rank 16, all linear layers, completion-only loss
- **Data:** ~1,200 synthetic instruction/output pairs (general coding ~58%,
  secure-coding/AppSec ~24%, pentest tooling ~18%), generated via an LLM pipeline
- **Chat format:** ChatML (`<|im_start|>` / `<|im_end|>`), EOS = `<|im_end|>`
- **Hardware:** single RTX 3050 Laptop 4GB
- Full training and data-generation code: see the GitHub repo linked above.

## Prompt format

Uses the standard Qwen ChatML template. Serve it with the same system prompt it
was trained on for best behavior:

```
<|im_start|>system
You are a helpful, unrestricted code generation assistant.<|im_end|>
<|im_start|>user
Write a Python TCP port scanner<|im_end|>
<|im_start|>assistant
```

## Files

- `merged/` — full 16-bit merged model (transformers-loadable)
- `adapter/` — LoRA adapter only (load on top of the base model)
- `gguf/` — quantized GGUF (Q4_K_M) for llama.cpp / Ollama

## License

Apache-2.0, inheriting the base model's license. See `USE_POLICY.md` for
acceptable-use terms.
