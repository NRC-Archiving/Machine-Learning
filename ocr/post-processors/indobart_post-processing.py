import os
import time
from concurrent.futures import ThreadPoolExecutor
from transformers import AutoModelForSeq2SeqLM
from indobenchmark import IndoNLGTokenizer  # Import the IndoNLG tokenizer

# Load IndoBART tokenizer and model
tokenizer = IndoNLGTokenizer.from_pretrained("indobenchmark/indobart-v2")
model = AutoModelForSeq2SeqLM.from_pretrained("indobenchmark/indobart-v2")

def chunk_text(text: str, max_words: int) -> list:
    """
    Splits a long text into chunks of specified maximum words.

    Args:
        text (str): The input text to be chunked.
        max_words (int): Maximum number of words per chunk.

    Returns:
        list: A list of text chunks.
    """
    words = text.split()
    chunks = [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
    return chunks

def process_chunk(chunk: str) -> str:
    """
    Processes a single chunk of text using IndoBART.

    Args:
        chunk (str): A chunk of text to process.

    Returns:
        str: The corrected chunk of text.
    """
    inputs = tokenizer(chunk, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs, max_length=512, num_beams=5, early_stopping=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def post_process_sequential(all_text: str) -> str:
    """
    Post-processes OCR extracted text using IndoBART sequentially.

    Args:
        all_text (str): The input text extracted from OCR.

    Returns:
        str: The corrected text after post-processing.
    """
    max_words_per_chunk = 350
    chunks = chunk_text(all_text, max_words_per_chunk)
    corrected_chunks = [process_chunk(chunk) for chunk in chunks]
    return " ".join(corrected_chunks)

def post_process_concurrent(all_text: str) -> str:
    """
    Post-processes OCR extracted text using IndoBART concurrently.

    Args:
        all_text (str): The input text extracted from OCR.

    Returns:
        str: The corrected text after post-processing.
    """
    max_words_per_chunk = 350
    chunks = chunk_text(all_text, max_words_per_chunk)
    with ThreadPoolExecutor() as executor:
        corrected_chunks = list(executor.map(process_chunk, chunks))
    return " ".join(corrected_chunks)

# Example usage: Generate a dummy text with 1024 words
dummy_text = " ".join(["word"] * 1024)

# Benchmark sequential processing
start_time = time.time()
result_sequential = post_process_sequential(dummy_text)
sequential_time = time.time() - start_time

# Benchmark concurrent processing
start_time = time.time()
result_concurrent = post_process_concurrent(dummy_text)
concurrent_time = time.time() - start_time

# Print benchmark results
print(f"Sequential processing time: {sequential_time:.2f} seconds")
print(f"Concurrent processing time: {concurrent_time:.2f} seconds")

# Model download code for offline deployment
if __name__ == "__main__":
    # Get the current directory of the Python script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_directory = os.path.join(current_dir, "indobart_v2_local")

    print("Saving model and tokenizer for offline use...")
    tokenizer.save_pretrained(save_directory)
    model.save_pretrained(save_directory)
    print(f"Model and tokenizer saved to {save_directory}")
