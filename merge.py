from unsloth import FastLanguageModel

# Load the adapter on top of the SAME base it was trained on (4-bit).
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "lora_model",
    max_seq_length = 512,
    dtype = None,
    load_in_4bit = True,   # match training; Unsloth handles the merge correctly
)

# Force eos to <|im_end|> so the model stops correctly (bakes into config + GGUF).
im_end = tokenizer.convert_tokens_to_ids("<|im_end|>")
tokenizer.eos_token = "<|im_end|>"
model.config.eos_token_id = im_end
model.generation_config.eos_token_id = im_end

# Merge to 16-bit and save the full model.
model.save_pretrained_merged(
    "uncensored-qwen-coder",
    tokenizer,
    save_method = "merged_16bit",
)

# Export GGUF (q4_k_m) for llama.cpp / Ollama.
model.save_pretrained_gguf(
    "uncensored-qwen-coder-gguf",
    tokenizer,
    quantization_method = "q4_k_m",
)

print("Done -> uncensored-qwen-coder/ and uncensored-qwen-coder-gguf/")
