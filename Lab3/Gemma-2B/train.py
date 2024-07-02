import torch, datasets
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

# Maximum sequence length
max_seq_length = 2048

# Hugging Face model id
model_id = "google/gemma-2b"

# BitsAndBytesConfig int-4 config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    quantization_config=bnb_config,
)
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.unk_token
tokenizer.padding_side = "right"

# Load the dataset
trainingData = datasets.load_dataset(
    "json", data_files="../dataset/train.json", split="train"
)

texts = []
for data in tqdm(trainingData):
    headline = data["headline"]
    body = data["body"]
    text = f"<bos><|im_start|>system\nYou are reporter.<|im_end|><|im_start|>user\nContent: {body}\nHeadline: <|im_end|><|im_start|>assistant\n{headline}<|im_end|>\n<eos>"
    if len(tokenizer(text).input_ids) > max_seq_length:
        continue
    texts.append(text)

dataset = datasets.Dataset.from_dict({"text": texts})


from peft import LoraConfig

# LoRA config
peft_config = LoraConfig(
    lora_alpha=16,
    lora_dropout=0.05,
    r=64,
    bias="none",
    task_type="CAUSAL_LM",
    # target_modules="all-linear",
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
    ],
)

from transformers import TrainingArguments

args = TrainingArguments(
    output_dir="result",
    num_train_epochs=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    gradient_checkpointing=True,
    optim="adamw_torch_fused",
    logging_steps=50,
    save_steps=50,
    bf16=True,
    learning_rate=2e-4,
    max_grad_norm=0.3,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    push_to_hub=False,
)

from trl import SFTTrainer

trainer = SFTTrainer(
    model=model,
    args=args,
    train_dataset=dataset,
    dataset_text_field="text",
    peft_config=peft_config,
    max_seq_length=max_seq_length,
    tokenizer=tokenizer,
    packing=True,
    dataset_kwargs={
        "add_special_tokens": False,
        "append_concat_token": False,
    },
)

# start training
trainer.train()

# save model id
save_model_id = "gemma-2b-tuned"

# save model
trainer.save_model(save_model_id)
