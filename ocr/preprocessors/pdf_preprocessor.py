import cv2
import numpy as np
from pdf2image import convert_from_path
from pytesseract import image_to_string
from PIL import Image
import os
import multiprocessing  
import concurrent.futures  
import time

# Import preprocessing modules
from preprocessors.background_removal import remove_background
from preprocessors.contrast_enhancement import enhance_contrast
from preprocessors.image_denoising import denoise_image
from preprocessors.adaptive_thresholding import apply_adaptive_thresholding
from preprocessors.deskewing import deskew_image
from preprocessors.upscaling import upscale_image
from preprocessors.crop_letterhead import crop_letterhead

def preprocess_image(image, doc_type=None):
    """Preprocesses a single image while ensuring it remains grayscale throughout."""
    start_time = time.time()
    
    # Step 1 Background Removal for specific type of document
    if doc_type in ["legalitas"]:
        image = remove_background(image)

    if doc_type in ["pengurus", "pemegang_saham"]:
        image = remove_background(image)
        image = apply_adaptive_thresholding(image)
        return image
    
    if doc_type in ["tenaga_ahli"]:
        image = remove_background(image)
        image = apply_adaptive_thresholding(image)
        image = deskew_image(image)
        return image
    
    # Step 2: Convert to grayscale
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # For CV and Pengurus only need 
    if doc_type in ["cv"]:
        image = enhance_contrast(image)
        image = apply_adaptive_thresholding(image, method='trunc')
        image = upscale_image(image)
        return image  

    # Step 3: Enhance Contrast
    image = enhance_contrast(image)

    # Step 4: Reduce Noise
    image = denoise_image(image)

    # Step 5: Apply Adaptive Thresholding (Binarization)
    image = apply_adaptive_thresholding(image, method="mean")

    # Step 6: Deskewing
    image = deskew_image(image)

    # Step 7: Upscaling
    image = upscale_image(image)

    # Additional step to crop letterhead from letter type document
    if doc_type in ["surat_masuk", "surat_keluar"]:
        image = crop_letterhead(image)

    # Double check to ensure final image is grayscale before returning
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return image


def ocr_extract(image, doc_type=None):
    """Runs OCR on a single grayscale image, using --psm 4 only for 'cv' documents."""
    config = "--psm 4" if doc_type == ["cv","tenaga_ahli"] else None  # Gunakan None jika tidak ada config

    if config:
        return image_to_string(Image.fromarray(image), config=config)
    else:
        return image_to_string(Image.fromarray(image))  


def extract_text_from_pdf(pdf_path, doc_type=None, dpi=300):
    """Extracts text from a PDF file using multi-processing & multi-threading, limited to first three pages."""
    try:
        # Step 1: Convert PDF to images (only first 3 pages)
        images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=4)
        if not images:
            raise ValueError("No images were extracted from the PDF.")

        # Step 2: Validate images before processing
        valid_images = []
        for img in images:
            try:
                np_img = np.array(img)
                if np_img is None or np_img.size == 0:
                    print(f"Warning: Skipping empty or invalid image.")
                    continue
                valid_images.append(np_img)
            except Exception as e:
                print(f"Error converting image to numpy array: {e}")
                continue

        if not valid_images:
            raise ValueError("No valid images available for processing.")

        # Step 3: Use Multi-Processing for Image Preprocessing
        with multiprocessing.Pool(processes=os.cpu_count()) as pool:
            processed_images = pool.starmap(preprocess_image, [(img, doc_type) for img in valid_images])

        # Step 4: Validate Processed Images
        processed_images = [img for img in processed_images if img is not None and img.size > 0]
        if not processed_images:
            raise ValueError("All images failed to process.")

        # Step 5: Use Multi-Threading for OCR Extraction
        with concurrent.futures.ThreadPoolExecutor() as executor:
            extracted_texts = list(executor.map(lambda img: ocr_extract(img, doc_type=doc_type), processed_images))

        text = "\n\n".join(extracted_texts).strip()
        text = text.replace(';', ':').replace('=', ':').replace('>', ':').replace('|','I').replace('!','1')

    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {e}")

    finally:
        # Remove the uploaded PDF file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    print(text)
    return text
