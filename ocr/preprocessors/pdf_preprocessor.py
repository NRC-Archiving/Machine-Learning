import cv2
import numpy as np
from pdf2image import convert_from_path
from pytesseract import image_to_string
from PIL import Image
import os
import multiprocessing  # ✅ Multi-Processing for Preprocessing
import concurrent.futures  # ✅ Multi-Threading for OCR Extraction
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
    print(f"Before preprocessing - Type: {type(image)}, Shape: {image.shape if hasattr(image, 'shape') else 'No Shape'}")

    # Step 1: Background Removal (Only for specific document types)
    if doc_type in ["tenaga_ahli", "legalitas"]:
        image = remove_background(image)

    if doc_type in ["pengurus", "pemegang_saham"]:
        image = remove_background(image)
        image = apply_adaptive_thresholding(image)
        return image
    
    # Step 2: Convert to grayscale (Ensuring consistency)
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    print(f"Converted to grayscale - Shape: {image.shape}")
    
    # If document type is "cv", only perform grayscale and upscaling, then return
    if doc_type in ["cv", "pengurus"]:
        #image = deskew_image(image)
        #image = upscale_image(image)
        print(f"After upscaling - Shape: {image.shape}")
        return image  # Skip other preprocessing steps

    # Step 3: Enhance Contrast
    image = enhance_contrast(image)
    print(f"After contrast enhancement - Shape: {image.shape}")

    # Step 4: Reduce Noise
    image = denoise_image(image)
    print(f"After denoising - Shape: {image.shape}")

    # Step 5: Apply Adaptive Thresholding (Binarization)
    image = apply_adaptive_thresholding(image, method="mean")
    print(f"After thresholding - Shape: {image.shape}")

    # Step 6: Deskewing
    image = deskew_image(image)
    print(f"After deskewing - Shape: {image.shape}")

    # Step 7: Upscaling
    image = upscale_image(image)
    print(f"After upscaling - Shape: {image.shape}")

    # Step 8: Crop Letterhead (Only for `surat_masuk` & `surat_keluar`)
    if doc_type in ["surat_masuk", "surat_keluar"]:
        image = crop_letterhead(image)
        print(f"After cropping - Shape: {image.shape}")

    # Ensure final image is grayscale before returning
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    print(f"Final grayscale image - Shape: {image.shape}")
    print(f'Full preprocessing time: {time.time() - start_time:.4f} seconds')
    return image


def ocr_extract(image):
    """Runs OCR on a single grayscale image."""
    return image_to_string(Image.fromarray(image))


def extract_text_from_pdf(pdf_path, doc_type=None, dpi=300):
    """Extracts text from a PDF file using multi-processing & multi-threading."""
    try:
        # ✅ Step 1: Convert PDF to images
        images = convert_from_path(pdf_path, dpi=dpi)
        if not images:
            raise ValueError("No images were extracted from the PDF.")

        # ✅ Step 2: Validate images before processing
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

        # ✅ Step 3: Use Multi-Processing for Image Preprocessing
        with multiprocessing.Pool(processes=os.cpu_count()) as pool:
            processed_images = pool.starmap(preprocess_image, [(img, doc_type) for img in valid_images])

        # ✅ Step 4: Validate Processed Images
        processed_images = [img for img in processed_images if img is not None and img.size > 0]
        if not processed_images:
            raise ValueError("All images failed to process.")

        # ✅ Step 5: Use Multi-Threading for OCR Extraction
        with concurrent.futures.ThreadPoolExecutor() as executor:
            extracted_texts = list(executor.map(ocr_extract, processed_images))

        text = "\n\n".join(extracted_texts).strip()
        text = text.replace(';', ':').replace('=', ':').replace('>', ':').replace('|','I').replace('!','1')

    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {e}")

    finally:
        # ✅ Remove the uploaded PDF file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    print(text)
    return text
