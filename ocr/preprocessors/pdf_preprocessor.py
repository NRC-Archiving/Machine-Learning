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
    """Preprocesses a single image while ensuring it remains grayscale throughout."""
    
    # ✅ Debugging: Print image properties before processing
    print(f"Before preprocessing - Type: {type(image)}, Shape: {image.shape if hasattr(image, 'shape') else 'No Shape'}")
    
    # Convert to grayscale at the start to ensure consistency
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    print(f"Converted to grayscale - Shape: {image.shape}")

    # Apply preprocessing steps
    image = denoise_image(image)
    print(f"After denoising - Shape: {image.shape}")

    image = apply_adaptive_thresholding(image)
    print(f"After thresholding - Shape: {image.shape}")

    image = deskew_image(image)
    print(f"After deskewing - Shape: {image.shape}")

    image = upscale_image(image)
    print(f"After upscaling - Shape: {image.shape}")

    image = crop_letterhead(image)
    print(f"After cropping - Shape: {image.shape}")

    # ✅ Ensure final image is grayscale before returning
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    print(f"Final grayscale image - Shape: {image.shape}")
    return image


def ocr_extract(image):
    """Runs OCR on a single grayscale image."""
    return image_to_string(Image.fromarray(image), lang="ind+eng")


def extract_text_from_pdf(pdf_path, doc_type=None, dpi=300):
    """Extracts text from a PDF file using hybrid optimization with multi-processing & multi-threading."""
    try:
        images = convert_from_path(pdf_path, dpi=dpi)

        # ✅ Step 1: Convert all images to grayscale immediately
        grayscale_images = [cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY) for img in images]

        # ✅ Step 2: Use Multi-Processing for Image Preprocessing
        with multiprocessing.Pool(processes=os.cpu_count()) as pool:
            processed_images = pool.starmap(preprocess_image, [(img, doc_type) for img in grayscale_images])

        # ✅ Step 3: Use Multi-Threading for OCR Extraction
        with concurrent.futures.ThreadPoolExecutor() as executor:
            extracted_texts = list(executor.map(ocr_extract, processed_images))

        text = "\n\n".join(extracted_texts).strip()

    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {e}")

    finally:
        # ✅ Remove the uploaded PDF file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    print(text)
    return text
