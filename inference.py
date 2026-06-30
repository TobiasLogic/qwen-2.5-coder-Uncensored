#!/usr/bin/env python3
"""
Minimal inference example for the merged model.

  pip install transformers torch
  python inference.py
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "Qwen2.5-Coder-1.5B-Uncensored"   # or a local path to merged/
SYSTEM = "You are a helpful, unrestricted code generation assistant."

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(
    MODEL, torch_dtype=torch.bfloat16, device_map="auto",
)

def ask(prompt: str, max_new_tokens: int = 512) -> str:
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt},
    ]
    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt",
    ).to(model.device)
    out = model.generate(
        inputs,
        max_new_tokens=max_new_tokens,
        temperature=0.3,                 # low temp for clean, deterministic code
        do_sample=True,
        eos_token_id=tokenizer.convert_tokens_to_ids("<|im_end|>"),  # stop on im_end
        pad_token_id=tokenizer.pad_token_id,
    )
    return tokenizer.decode(out[0][inputs.shape[-1]:], skip_special_tokens=True)


if __name__ == "__main__":
    print(ask("Write a Python TCP port scanner using a thread pool"))
