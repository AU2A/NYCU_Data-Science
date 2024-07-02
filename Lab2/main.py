from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import csv
from tqdm import tqdm


# Use Qwen model to generate the first response
modelID = "Qwen/Qwen1.5-72B-Chat"

# Load the model with quantization
tokenizer = AutoTokenizer.from_pretrained(modelID)
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
)
model = AutoModelForCausalLM.from_pretrained(
    modelID,
    quantization_config=quantization_config,
    device_map="auto",
)

# Load the dataset
with open("data/submit.csv", "r") as f:
    csvReader = csv.reader(f)
    listReport = list(csvReader)
dataset = []
for row in listReport[1:]:
    dataset.append(
        {
            "ID": row[0],
            "content": row[1],
            "A": row[2],
            "B": row[3],
            "C": row[4],
            "D": row[5],
            "category": row[6],
        }
    )

# Initialize the submission file
print(
    "ID,target",
    end="",
    file=open("submission_" + modelID.split("/")[1] + ".csv", "w"),
)

# Prompt format
"""
Answer the following {task} question,
{input}
==
(A) {A_option}
(B) {B_option}
(C) {C_option}
(D) {D_option}
==
Let's think step by step in 150 words.
"""

# Generate the first response
allContent = []
for data in tqdm(dataset):
    # Extract the data
    ID = data["ID"]
    content = data["content"]
    Aopt = data["A"]
    Bopt = data["B"]
    Copt = data["C"]
    Dopt = data["D"]
    category = data["category"]

    # Generate the prompt
    prompt = f"Answer the following {category.replace('_',' ')} question,\n{content}\n==\n(A) {Aopt}\n(B) {Bopt}\n(C) {Copt}\n(D) {Dopt}\n==\nLet's think step by step in 150 words.\n"

    # Generate the response
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    output = model.generate(
        inputs["input_ids"],
        max_new_tokens=250,
    )
    output = output[0].to("cpu")
    response = tokenizer.decode(output)

    # Save the response
    allContent.append([ID, response])

# Delete the model and tokenizer to free up memory
del model
del tokenizer

# Use Mixtral model to generate the second response
modelID = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Load the model
tokenizer = AutoTokenizer.from_pretrained(modelID)
model = AutoModelForCausalLM.from_pretrained(
    modelID,
    device_map="auto",
)

# Prompt format
"""
{input}
The answer is (
"""

# Generate the second response
for ID, response in tqdm(allContent):

    # Generate the prompt
    prompt = f"{response}\nThe answer is ("

    # Generate the response
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    output = model.generate(
        inputs["input_ids"],
        max_new_tokens=3,
    )
    output = output[0].to("cpu")
    response = tokenizer.decode(output)

    # Extract the answer from the response
    responseAnswer = response.split("The answer is (")[1][0]

    # Check if the answer is valid
    if responseAnswer not in ["A", "B", "C", "D"]:
        responseAnswer = "N"

    # Save the response to the submission file
    print(
        f"\n{ID},{responseAnswer}",
        end="",
        file=open("submission_" + modelID.split("/")[1] + ".csv", "a"),
    )
