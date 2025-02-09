import time
import cv2
import numpy as np

def crop_letterhead(image):
    """    
    start_time = time.time()
    height, width = image.shape[:2]
    min_remaining_height = int(height * 0.90)
    safe_margin = int(height * 0.05)
    """
    start_time = time.time()
    height, width = image.shape[:2]
    min_remaining_height = int(height * 0.90)
    safe_margin = int(height * 0.05)
    
    
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_y = 0
    upper_region = int(height * 0.05)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if y < upper_region and w > width * 0.6 and h > 10:
            max_y = max(max_y, y + h)

    if max_y > 0 and height - (max_y + safe_margin) > min_remaining_height:
        result = image[max_y + safe_margin:, :]
    else:
        result = image

    print(f'Crop letterhead time: {time.time() - start_time:.4f} seconds')
    return result
