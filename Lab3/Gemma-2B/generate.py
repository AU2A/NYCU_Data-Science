# Importing required libraries
import torch, json, datasets
from tqdm import tqdm
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer, pipeline, BitsAndBytesConfig

# Model ID
peft_model_id = "gemma-2b-tuned"

# Parameters
endToken = "<|im_end|>"
datasetPath = "../dataset/testOriginal.json"


# Prompt template
def promptByTemplate(body):
    return f"<bos><|im_start|>system\nYou are reporter.<|im_end|><|im_start|>user\nContent: {body}\nHeadline: <|im_end|><|im_start|>assistant\n"


# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(peft_model_id)

# Quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

# Load Model with PEFT adapter
model = AutoPeftModelForCausalLM.from_pretrained(
    peft_model_id,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    quantization_config=bnb_config,
)

model.eval()

# Get token id for end of conversation
eos_token = tokenizer(endToken, add_special_tokens=False)["input_ids"][0]

# Load testing data
testingData = datasets.load_dataset("json", data_files=datasetPath, split="train")


# Inference function
def test_inference(testingData):
    body = testingData["body"]
    prompt = promptByTemplate(body)

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs,
        max_new_tokens=32,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.95,
        eos_token_id=eos_token,
        pad_token_id=eos_token,
    )

    gc.collect()
    torch.cuda.empty_cache()

    outputs = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return outputs[len(prompt) - 3 : -1].strip()


# Create json
print("", end="", file=open("preds.json", "w", encoding="utf-8"))

# Inference
for prompt in tqdm(testingData):
    response = test_inference(prompt)
    print(
        json.dumps({"headline": response}, ensure_ascii=False),
        file=open("preds.json", "a", encoding="utf-8"),
    )
