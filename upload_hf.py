#!/usr/bin/env python3
"""
Upload the fine-tuned model to HuggingFace Hub: adapter + merged + GGUF.

Setup:
  pip install huggingface_hub
  hf auth login          # paste a token with WRITE scope from hf.co/settings/tokens

Then edit REPO_ID below and run:  python upload_hf.py
"""

from huggingface_hub import HfApi, create_repo
import os

# -----------------------------------------------------------------
REPO_ID   = "TobiasLogic/qwen-2.5-coder-Uncensored"   # <-- change to your repo
LOCAL = {
    "adapter": "lora_model",                                              # LoRA adapter folder
    "merged":  "uncensored-qwen-coder",                                   # 16-bit merged model folder (optional)
    "gguf":    "uncensored-qwen-coder-gguf_gguf/qwen2.5-coder-1.5b.Q4_K_M.gguf",  # GGUF file
}
MODEL_CARD = "MODEL_CARD.md"                  # becomes the repo's README.md
USE_POLICY = "USE_POLICY.md"
# -----------------------------------------------------------------

api = HfApi()
create_repo(REPO_ID, repo_type="model", exist_ok=True)
print(f"[*] Repo ready: https://huggingface.co/{REPO_ID}")

# Model card -> README.md at repo root
if os.path.exists(MODEL_CARD):
    api.upload_file(path_or_fileobj=MODEL_CARD, path_in_repo="README.md", repo_id=REPO_ID)
    print("[+] uploaded model card -> README.md")
if os.path.exists(USE_POLICY):
    api.upload_file(path_or_fileobj=USE_POLICY, path_in_repo="USE_POLICY.md", repo_id=REPO_ID)
    print("[+] uploaded USE_POLICY.md")

# Adapter folder -> adapter/
if os.path.isdir(LOCAL["adapter"]):
    api.upload_folder(folder_path=LOCAL["adapter"], path_in_repo="adapter", repo_id=REPO_ID)
    print("[+] uploaded adapter/")

# Merged model folder -> merged/   (skip the GGUF if it lives inside)
if os.path.isdir(LOCAL["merged"]):
    api.upload_folder(
        folder_path=LOCAL["merged"], path_in_repo="merged", repo_id=REPO_ID,
        ignore_patterns=["*.gguf"],
    )
    print("[+] uploaded merged/")

# GGUF file -> gguf/
if os.path.exists(LOCAL["gguf"]):
    api.upload_file(
        path_or_fileobj=LOCAL["gguf"],
        path_in_repo=f"gguf/{os.path.basename(LOCAL['gguf'])}",
        repo_id=REPO_ID,
    )
    print("[+] uploaded GGUF")

print(f"\n[+] Done -> https://huggingface.co/{REPO_ID}")
