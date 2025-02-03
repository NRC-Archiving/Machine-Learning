import cv2
import numpy as np

def crop_letterhead(image):
    """
    Improved function to crop only the letterhead while preserving the date and other important text.
    - Works **entirely in grayscale**.
    - Adds a safe margin to avoid cutting off necessary content.
    - Ensures only wide and meaningful letterheads are cropped.
    """

    height, width = image.shape[:2]
    min_remaining_height = int(height * 0.90)  # Ensure at least 90% of the document remains
    safe_margin = int(height * 0.05)  # Fixed safe margin (5%)
    
    # ✅ Ensure the image is grayscale
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to detect text and objects
    _, thresh = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_y = 0
    upper_region = int(height * 0.10)  # Limit search to the top 10% of the document

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if y < upper_region and w > width * 0.8 and h > 30:  # Must be a meaningful letterhead
            max_y = max(max_y, y + h)

    # Apply final cropping
    if max_y > 0 and height - (max_y + safe_margin) > min_remaining_height:
        return image[max_y + safe_margin:, :]
    else:
        return image
