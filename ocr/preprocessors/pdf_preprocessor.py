import os
import cv2
from tempfile import TemporaryDirectory
from pdf2image import convert_from_path
from pytesseract import image_to_string
from PIL import Image

def preprocess_image(image_path, method="trunc"):
    try:
        # Load the image and convert to grayscale
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply preprocessing based on the method
        if method == "trunc":
            gray = cv2.threshold(gray, 127, 255, cv2.THRESH_TRUNC)[1]

        # Save the preprocessed image temporarily
        temp_filename = f"{os.getpid()}.png"
        cv2.imwrite(temp_filename, gray)

        # Extract text using OCR
        text = image_to_string(Image.open(temp_filename))

        # Clean up temporary file
        os.remove(temp_filename)

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
            extracted_text = []

            # Process each image and extract text
            for i, image_path in enumerate(image_paths):
                text = preprocess_image(image_path, preprocessing_method)
                extracted_text.append(f"--- Page {i + 1} ---\n{text}")

            return "\n\n".join(extracted_text).strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")
