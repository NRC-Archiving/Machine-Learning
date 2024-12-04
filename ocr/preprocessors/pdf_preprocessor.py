import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from pytesseract import image_to_string
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import asyncio

def preprocess_image(image, method="trunc"):
    try:
        if isinstance(image, str):  # If the input is a file path
            image = cv2.imread(image)
        else:  # If the input is a PIL image
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply preprocessing based on the method
        if method == "trunc":
            gray = cv2.threshold(gray, 127, 255, cv2.THRESH_TRUNC)[1]

        return gray
    except Exception as e:
        raise ValueError(f"Error during image preprocessing: {e}")

def ocr_image(image):
    try:
        # Convert OpenCV image to PIL format for OCR
        pil_image = Image.fromarray(image)
        text = image_to_string(pil_image)
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error during OCR: {e}")

def convert_pdf_to_images(pdf_path, dpi=300):
    try:
        return convert_from_path(pdf_path, dpi=dpi)
    except Exception as e:
        raise ValueError(f"Error converting PDF to images: {e}")

async def process_page_async(image, page_num, preprocessing_method="trunc"):
    try:
        processed_image = preprocess_image(image, preprocessing_method)
        text = ocr_image(processed_image)
        return f"--- Page {page_num + 1} ---\n{text}"
    except Exception as e:
        return f"--- Page {page_num + 1} ---\n[ERROR] {str(e)}"

async def extract_text_from_pdf_async(pdf_path, dpi=300, preprocessing_method="trunc"):
    try:
        # Convert PDF to images
        images = convert_pdf_to_images(pdf_path, dpi)

        # Select specific pages: first 7 and last 7 if more than 15
        total_pages = len(images)
        if total_pages > 15:
            images = images[:7] + images[-7:]

        # Process images concurrently
        tasks = [
            process_page_async(image, i, preprocessing_method)
            for i, image in enumerate(images)
        ]
        results = await asyncio.gather(*tasks)
        return "\n\n".join(results).strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {e}")

def extract_text_from_pdf(pdf_path, dpi=300, preprocessing_method="trunc"):
    try:
        # Use asyncio to process images asynchronously
        return asyncio.run(extract_text_from_pdf_async(pdf_path, dpi, preprocessing_method))
    except Exception as e:
        raise ValueError(f"Error in synchronous extraction: {e}")
