import cv2
import numpy as np
import time

def apply_adaptive_thresholding(image):
    start_time = time.time()  # Start time tracking

    # Ensure the image is grayscale
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(
        image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    end_time = time.time()  # End time tracking
    print(f"Time elapsed in adaptive_thresholding.py: {end_time - start_time:.4f} seconds")

    return thresh
