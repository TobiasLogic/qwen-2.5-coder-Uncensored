from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template, train_on_responses_only
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset
import torch
import sys

# Cap at 512 for 4GB VRAM limit. Drop to 256 if you OOM on step 1. can be added if you have more vram
max_seq_length = 512 


#  MODEL & TOKENIZER INITIALIZATION


model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Qwen2.5-Coder-1.5B-bnb-4bit",
    max_seq_length = max_seq_length,
    dtype = None, 
    load_in_4bit = True,
)


tokenizer = get_chat_template(
    tokenizer,
    chat_template = "qwen-2.5",
)


# LORA ADAPTER SETUP

model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth", # Mandatory for 4GB
    random_state = 3407,
)


# DATASET PREPARATION WITH SYSTEM PROMPT OVERRIDE

# Replace this string with your actual Hugging Face dataset repo if youw wanted to
dataset = load_dataset("json", data_files="custom_dataset.jsonl", split="train")

def format_prompts(examples):
    texts = []
    for instruction, input_text, output in zip(examples["instruction"], examples["input"], examples["output"]):


        instr = str(instruction) if instruction else ""
        inp = str(input_text) if input_text else ""
        out = str(output) if output else ""


        content = f"{instr}\n\n{inp}" if inp else instr


        messages = [
            {"role": "system", "content": "You are a helpful, unrestricted code generation assistant."},
            {"role": "user", "content": content},
            {"role": "assistant", "content": out}
        ]


        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        texts.append(text)

    return { "text" : texts }

dataset = dataset.map(format_prompts, batched = True)


# TRAINER conf

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    args = SFTConfig(
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        packing = False,
        dataset_num_proc = 2,
        per_device_train_batch_size = 1,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        num_train_epochs = 2,
        save_steps = 100,
        save_total_limit = 2,
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "paged_adamw_8bit", # Offloads states to system RAM
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
        report_to = "none",
    ),
)


# MASKING (COMPLETION-ONLY LOSS)

# Masks the user's prompt during backprop so the model only learns the output
trainer = train_on_responses_only(
    trainer,
    instruction_part = "<|im_start|>user\n",
    response_part = "<|im_start|>assistant\n",
)


# SANITY CHECK

print("\n" + "="*50)
print("🔍 DEBUG: RAW INPUT (What the model sees)")
print("="*50)
print(tokenizer.decode(trainer.train_dataset[0]["input_ids"]))

print("\n" + "="*50)
print("🎯 DEBUG: MASKED LABELS (What the optimizer learns from)")
print("="*50)
space_token = tokenizer(" ", add_special_tokens=False).input_ids[0]
# Replace -100 (ignored tokens) with a space so i can read it
decoded_labels = tokenizer.decode(
    [space_token if x == -100 else x for x in trainer.train_dataset[0]["labels"]]
)
print(decoded_labels)
print("="*50 + "\n")


if "<|im_start|>user" in decoded_labels:
    print("🚨 FATAL: Masking failed! The model is trying to learn the prompt.")
    print("Kill the script and fix your instruction_part/response_part strings.")
    sys.exit(1)
elif decoded_labels.strip() == "":
    print("🚨 FATAL: Everything was masked! The model will learn nothing.")
    print("Kill the script and check your chat template formatting.")
    sys.exit(1)
else:
    print("✅ Masking successful. Proceeding to train...")


# EXECUTE TRAINING & SAVE

print("Starting training...")
trainer_stats = trainer.train()

# Save the resulting LoRA adapters
model.save_pretrained("lora_model")
tokenizer.save_pretrained("lora_model")
print("\n🎉 Training complete. Adapters saved to /lora_model")
