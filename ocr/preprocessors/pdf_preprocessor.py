import os
import cv2
from tempfile import TemporaryDirectory
from pdf2image import convert_from_path
from pytesseract import image_to_string
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

def preprocess_image(image_path, method="trunc"):
    try:
        # Load the image and convert to grayscale
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply preprocessing based on the method
        if method == "trunc":
            gray = cv2.threshold(gray, 127, 255, cv2.THRESH_TRUNC)[1]

        # Encode the image in memory
        _, buffer = cv2.imencode(".png", gray)
        temp_image = Image.open(buffer)

        # Extract text using OCR
        text = image_to_string(temp_image)
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error during preprocessing: {str(e)}")

def convert_pdf_to_images(pdf_path, dpi=300, temp_dir=None):
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=dpi, output_folder=temp_dir)
        image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(temp_dir, f"page_{i + 1}.png")
            image.save(image_path)
            image_paths.append(image_path)
        return image_paths
    except Exception as e:
        raise ValueError(f"Error converting PDF to images: {str(e)}")

def extract_text_from_pdf(pdf_path, dpi=300, preprocessing_method="trunc"):
    try:
        with TemporaryDirectory() as temp_dir:
            # Convert PDF to images
            image_paths = convert_pdf_to_images(pdf_path, dpi, temp_dir)

            # Select specific pages: first 7 and last 7 if more than 15
            total_pages = len(image_paths)
            if total_pages > 15:
                selected_pages = image_paths[:7] + image_paths[-7:]
            else:
                selected_pages = image_paths

            extracted_text = []

            # Process images in parallel
            def process_page(image_path, page_num):
                text = preprocess_image(image_path, preprocessing_method)
                return f"--- Page {page_num + 1} ---\n{text}"

            with ThreadPoolExecutor() as executor:
                results = executor.map(
                    process_page,
                    selected_pages,
                    range(len(selected_pages))
                )

            # Collect results
            extracted_text.extend(results)

            return "\n\n".join(extracted_text).strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")
