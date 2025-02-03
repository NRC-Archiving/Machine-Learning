import cv2
import numpy as np
from pdf2image import convert_from_path
from pytesseract import image_to_string
from PIL import Image
import os
import multiprocessing  # ✅ Multi-Processing for Preprocessing
import concurrent.futures  # ✅ Multi-Threading for OCR Extraction

# Import preprocessing modules
from preprocessors.image_denoising import denoise_image
from preprocessors.adaptive_thresholding import apply_adaptive_thresholding
from preprocessors.deskewing import deskew_image
from preprocessors.upscaling import upscale_image
from preprocessors.crop_letterhead import crop_letterhead

def preprocess_image(image, doc_type=None):
    """Preprocesses a single image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply header cropping only on first page of "surat" documents
    if doc_type in ["surat_masuk", "surat_keluar"]:
        gray = crop_letterhead(gray)

    # Apply preprocessing steps
    upscaled = upscale_image(gray, scale=2)
    denoised = denoise_image(upscaled)
    thresholded = apply_adaptive_thresholding(denoised)
    deskewed = deskew_image(thresholded)

    return deskewed

def ocr_extract(image):
    """Runs OCR on a single image."""
    return image_to_string(Image.fromarray(image))

def extract_text_from_pdf(pdf_path, doc_type=None, dpi=300):
    """Extracts text from a PDF file using hybrid optimization."""
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        temp_image_paths = []  # Store temp images for cleanup

        # ✅ Step 1: Use Multi-Processing for Image Preprocessing
        with multiprocessing.Pool(processes=os.cpu_count()) as pool:
            processed_images = pool.starmap(preprocess_image, [(np.array(img), doc_type) for img in images])

        # ✅ Step 2: Use Multi-Threading for OCR Extraction
        with concurrent.futures.ThreadPoolExecutor() as executor:
            extracted_texts = list(executor.map(ocr_extract, processed_images))

        extracted_text = "\n\n".join(extracted_texts).strip()

    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {e}")

    finally:
        # ✅ Remove the uploaded PDF file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        # ✅ Remove all temporary images
        for temp_image in temp_image_paths:
            if os.path.exists(temp_image):
                os.remove(temp_image)

    return extracted_text
