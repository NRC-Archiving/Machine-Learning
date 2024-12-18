from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "indobenchmark/indobart-v2"
save_directory = "./model/indobart-v2"

# Download and save the model locally
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

tokenizer.save_pretrained(save_directory)
model.save_pretrained(save_directory)

print(f"Model and tokenizer saved to {save_directory}")
