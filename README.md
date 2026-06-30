# Uncensored Qwen-Coder Fine-tuning Pipeline

End-to-end pipeline for fine-tuning **Qwen2.5-Coder-1.5B** into a direct,
compliant coding assistant for software engineering, AppSec, and pentest-tooling
work — trained on a single 4GB laptop GPU with [Unsloth](https://github.com/unslothai/unsloth).

> **Scope & intent:** This produces a coding model that doesn't refuse or moralize
> on legitimate security tooling (scanners, fuzzers, PoCs, secure-coding fixes).
> It is built for **authorized** security work, CTFs, and learning. It is not for
> producing weaponized malware. See `USE_POLICY.md`. Use it lawfully.

Model weights: **[on HuggingFace](https://huggingface.co/Htfi)** ·
Author: **[TobiasLogic](https://github.com/TobiasLogic)**

## What's here

| File | What it does |
|------|--------------|
| `make_topics.py` | Combinatorially generates ~1,200 diverse training topics across general coding / AppSec / pentest, at a tuned ratio |
| `generate_dataset.py` | Resumable LLM pipeline (OpenRouter) that turns topics into `{instruction, input, output}` JSONL, with retry/backoff and dedup |
| `train.py` | QLoRA fine-tune via Unsloth: 4-bit, completion-only loss, ChatML, with a masking sanity-check |
| `merge.py` | Merges the LoRA adapter to 16-bit and exports GGUF |
| `data/sample_dataset.jsonl` | A small sample of the generated data (full dataset in `data/`) |
| `Modelfile` | Ollama config with correct ChatML template + stop tokens |

## Pipeline overview

```
make_topics.py  ->  topics.txt
generate_dataset.py  ->  custom_dataset.jsonl     (uses an OpenRouter API key)
train.py  ->  lora_model/                          (QLoRA on 4GB)
merge.py  ->  merged model + GGUF
ollama create  ->  runnable local model
```

## Reproduce it

```bash
# 0. Environment (Linux, NVIDIA GPU)
python -m venv env && source env/bin/activate
pip install torch
pip install unsloth
pip install --no-deps xformers peft accelerate bitsandbytes trl

# 1. Generate topics
python make_topics.py                         # writes topics.txt (~1200)

# 2. Generate the dataset
export OPENROUTER_API_KEY="sk-or-v1-..."
python generate_dataset.py                    # writes custom_dataset.jsonl

# 3. Train
python train.py                               # QLoRA, ~20 min on RTX 3050

# 4. Merge + export GGUF
python merge.py

# 5. Serve locally
ollama create my-coder -f Modelfile
ollama run my-coder
```

## Key technical notes

- **Base, not Instruct.** Starting from `Qwen2.5-Coder-1.5B` base means there's no
  refusal layer to remove — behavior is defined entirely by the (refusal-free)
  training data.
- **EOS must be `<|im_end|>`.** The base model's EOS is `<|endoftext|>` (151643);
  training uses ChatML so the model emits `<|im_end|>` (151645). `config.json`,
  `generation_config.json`, and the GGUF metadata all must say 151645 or the model
  never stops generating. `merge.py` forces this.
- **Completion-only loss.** Only the assistant response is trained on; the prompt
  is masked. `train.py` includes a sanity-check that prints masked labels.
- **Data quality is everything.** The model is exactly as good as the topics in
  `make_topics.py`. Edit the marked lists to target your own stack.

## Hardware

Trained on: ASUS TUF A15 — Ryzen 7 7435HS, RTX 3050 Laptop 4GB, 16GB RAM,
EndeavourOS. Anything with ≥4GB VRAM should work.

## License

Apache-2.0. See `LICENSE` and `USE_POLICY.md`.
