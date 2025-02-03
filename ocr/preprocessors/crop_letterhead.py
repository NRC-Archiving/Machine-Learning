import cv2
import numpy as np

def crop_letterhead(image):
    """
    Crops the letterhead only if detected at the top of the page.
    Ensures cropping is done horizontally, not vertically.
    """
    height, width = image.shape[:2]

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding for better letterhead detection
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_y = 0  # Track the lowest boundary of the detected letterhead

    # Process contours to detect letterhead only in the upper 15% region
    upper_region = int(height * 0.15)  # Top 15% of the image

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # Check if the detected component is within the upper region
        if y < upper_region and h > 30:  # Ensures it's a meaningful letterhead, not noise
            max_y = max(max_y, y + h)

    # Crop only the top portion while preserving full width
    if max_y > 0:
        return image[max_y:, :]  # Crop everything below the letterhead
    else:
        return image  # Return original image if no letterhead is detected
