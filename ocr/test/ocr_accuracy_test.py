import os
import sys
import difflib
import re
from preprocessors.pdf_preprocessor import extract_text_from_pdf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_levenshtein_similarity(text1, text2):
    return difflib.SequenceMatcher(None, text1, text2).ratio()

def compute_word_accuracy(text1, text2):
    words1 = re.findall(r'\w+', text1.lower())
    words2 = re.findall(r'\w+', text2.lower())
    common = set(words1) & set(words2)
    return len(common) / max(len(words1), len(words2), 1)

def compute_cosine_similarity(text1, text2):
    vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    return cosine_similarity(vectorizer[0], vectorizer[1])[0][0]

def test_ocr_extraction(pdf_path, expected_txt_path):
    """
    This test is performed on three different PDF types:
    1. test_native.pdf  - A PDF generated from document conversion (ideal quality)
    2. test_scan.pdf    - A high-quality scanned document
    3. test_photo.pdf   - A scanned document using a phone camera (lower quality)
    """
    extracted_text = extract_text_from_pdf(pdf_path)
    with open(expected_txt_path, 'r', encoding='utf-8') as f:
        expected_text = f.read()
    
    levenshtein_score = compute_levenshtein_similarity(extracted_text, expected_text)
    word_accuracy_score = compute_word_accuracy(extracted_text, expected_text)
    cosine_sim_score = compute_cosine_similarity(extracted_text, expected_text)
    
    print(f"\nOCR Extraction Accuracy Scores for {pdf_path}:")
    print(f"- Levenshtein Similarity: {levenshtein_score * 100:.2f}%")
    print(f"- Word-Level Accuracy: {word_accuracy_score * 100:.2f}%")
    print(f"- Cosine Similarity: {cosine_sim_score * 100:.2f}%")

if __name__ == "__main__":
    test_files = [
        ("test_native_cv.pdf", "test_native_cv.txt"),
        ("test_scan_cv.pdf", "test_scan_cv.txt"),
        ("test_photo_cv.pdf", "test_photo_cv.txt")
    ]
    
    for pdf, txt in test_files:
        if os.path.exists(pdf) and os.path.exists(txt):
            test_ocr_extraction(pdf, txt)
        else:
            print(f"Skipping {pdf} - missing corresponding text file {txt}")
