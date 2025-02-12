from datasets import load_dataset
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.meteor_score import meteor_score
from sacrebleu import corpus_ter, corpus_chrf
from transformers import MarianMTModel, MarianTokenizer

def evaluate_translation(reference_texts, translated_texts):
    assert len(reference_texts) == len(translated_texts), "Mismatch in number of reference and translated texts"
    
    from nltk.translate.bleu_score import SmoothingFunction
    smoothie = SmoothingFunction().method1
    bleu_scores = [sentence_bleu([ref.split()], trans.split(), smoothing_function=smoothie) for ref, trans in zip(reference_texts, translated_texts)]
    avg_bleu = sum(bleu_scores) / len(bleu_scores)
    
    meteor_scores = [meteor_score([ref.split()], trans.split()) for ref, trans in zip(reference_texts, translated_texts)]
    avg_meteor = sum(meteor_scores) / len(meteor_scores)
    
    ter_score = corpus_ter(translated_texts, [reference_texts]).score
    chrf_score = corpus_chrf(translated_texts, [reference_texts]).score
    
    return {
        "BLEU": avg_bleu,
        "METEOR": avg_meteor,
        "TER": ter_score,
        "chrF": chrf_score
    }

if __name__ == "__main__":
    print("Loading dataset...")
    dataset = load_dataset("indonlp/NusaX-MT", "ind-eng", trust_remote_code=True)

    test_data = dataset["test"].select(range(100))  # Limit to first 1000 sentences
    print("Available columns:", test_data.column_names)  # Debugging column names
    reference_texts = [item["text_2"] for item in test_data]  # Adjusted based on available columns  # Adjust based on column names
    original_texts = [item["text_1"] for item in test_data]  # Adjusted based on available columns  # Adjust based on column names

    print("Translating text...")
    model_name = "Helsinki-NLP/opus-mt-id-en"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

def translate_texts(texts):
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
    translated = model.generate(**inputs)
    return [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
    translated_texts = translate_texts(original_texts)
    for i, text in enumerate(original_texts):
        translated_texts.append(translator.translate(text))
        if i % 10 == 0:
            print(f"Translated {i}/{len(original_texts)} sentences...")

    print("Evaluating translation...")
    scores = evaluate_translation(reference_texts, translated_texts)

    print("Translation Evaluation Scores:")
    print(scores)
