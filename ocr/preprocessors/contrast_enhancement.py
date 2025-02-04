import cv2
import time

def enhance_contrast(image):
    """
    Enhances contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).
    Helps improve text clarity for OCR.
    """
    start_time = time.time()
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    print(f'Contras enhancement time: {time.time() - start_time:.4f} seconds')
    return clahe.apply(image) # Assumes input is already grayscale
