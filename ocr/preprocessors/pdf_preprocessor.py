from PIL import Image
import os
import cv2
import numpy as np
from pdf2image import convert_from_path
import pytesseract
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from crop_letterhead import crop_image_body


def preprocess_image(image, method="trunc", remove_lines=False):
    """
    Preprocess an image by applying a specified preprocessing method.

    Args:
        image (str or PIL.Image.Image): Input image or file path to the image.
        method (str): Preprocessing method to apply. Default is "trunc".
        remove_lines (bool): Whether to remove horizontal lines from the image.

    Returns:
        np.ndarray: Preprocessed image.
    """
    try:
        if isinstance(image, str):  # If the input is a file path
            image = cv2.imread(image)
        else:  # If the input is a PIL image
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        if remove_lines:
            # Morphological operations to remove horizontal lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            detect_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
            contours, _ = cv2.findContours(detect_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                cv2.drawContours(gray, [contour], -1, (255, 255, 255), thickness=cv2.FILLED)

        # Apply preprocessing based on the method
        if method == "trunc":
            gray = cv2.threshold(gray, 127, 255, cv2.THRESH_TRUNC)[1]

        return gray
    except Exception as e:
        raise ValueError(f"Error during image preprocessing: {e}")

def convert_pdf_to_images(pdf_path: str, output_folder: str):
    """
    Convert PDF to images using pdf2image.

    Args:
        pdf_path (str): Path to the input PDF file.
        output_folder (str): Directory to save the resulting images.

    Returns:
        List[str]: Paths to the generated image files.
    """
    print("Converting PDF to images...")
    images = convert_from_path(pdf_path)
    image_paths = []
    
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
        image.save(image_path, "JPEG")
        image_paths.append(image_path)
    print(f"Saved images to {output_folder}")
    return image_paths

def process_image(image_path, crop_ratio, doc_type, preprocessing_method, remove_lines):
    """
    Process a single image: Crop, preprocess, and perform OCR.
    """
    if doc_type in ["surat_keluar", "surat_masuk"]:
        cropped_image_path = image_path.replace(".jpg", "_cropped.jpg")
        print(f"Document type '{doc_type}' detected. Cropping body...")
        crop_image_body(image_path, cropped_image_path, crop_ratio)
        image_path = cropped_image_path
    else:
        print(f"Document type '{doc_type}' does not require cropping. Skipping cropping step.")

    # Preprocess the image
    preprocessed_image = preprocess_image(image_path, method=preprocessing_method, remove_lines=remove_lines)
    preprocessed_image_path = image_path.replace(".jpg", "_preprocessed.jpg")
    cv2.imwrite(preprocessed_image_path, preprocessed_image)

    # Perform OCR
    text = pytesseract.image_to_string(Image.fromarray(preprocessed_image))
    return text

def preprocess_pdf_and_extract_text(pdf_path: str, output_folder: str, crop_ratio: float = 0.2, doc_type: str = "unknown", preprocessing_method: str = "trunc", remove_lines: bool = False):
    """
    Full pipeline: Convert PDF to images, conditionally crop body, preprocess images, and extract text via OCR.

    Args:
        pdf_path (str): Path to the input PDF file.
        output_folder (str): Directory to save intermediate and output files.
        crop_ratio (float): Ratio of the image height to crop from the top.
        doc_type (str): Type of the document to conditionally apply cropping.
        preprocessing_method (str): Image preprocessing method to apply before OCR.
        remove_lines (bool): Whether to remove horizontal lines from the images.

    Returns:
        str: Extracted text from the entire PDF.
    """
    images = convert_from_path(pdf_path)

    # Modify page selection based on doc_type
    total_pages = len(images)
    if doc_type == "keuangan":
        images = images[:7]  # Limit to the first 7 pages
    elif total_pages > 15:  # Default behavior for other document types
        images = images[:5] + images[-5:]

    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
        image.save(image_path, "JPEG")
        image_paths.append(image_path)

    # Parallel processing
    full_text = ""
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        results = executor.map(process_image, image_paths, [crop_ratio]*len(image_paths), 
                               [doc_type]*len(image_paths), [preprocessing_method]*len(image_paths), [remove_lines]*len(image_paths))
        for text in results:
            full_text += text + "\n"

    return full_text
