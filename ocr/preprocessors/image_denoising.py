import cv2
import time
import numpy as np

def fast_denoise(image, downscale_factor=2):
    """
    Optimized denoising function:
    - Uses fastNlMeansDenoising but adds Bilateral Filtering to retain sharp text.
    - Keeps text edges intact for better OCR accuracy.
    """

    start_time = time.time()

    # Step 1: Downscale image
    height, width = image.shape[:2]
    small_image = cv2.resize(image, (width // downscale_factor, height // downscale_factor), interpolation=cv2.INTER_LINEAR)

    # Step 2: Apply fast denoising (lower strength to preserve text)
    denoised_small = cv2.fastNlMeansDenoising(small_image, None, h=5, templateWindowSize=7, searchWindowSize=15)

    # Step 3: Apply Bilateral Filtering (to preserve edges)
    denoised_small = cv2.bilateralFilter(denoised_small, d=9, sigmaColor=75, sigmaSpace=75)

    # Step 4: Upscale back to original size
    denoised = cv2.resize(denoised_small, (width, height), interpolation=cv2.INTER_LINEAR)

    end_time = time.time()
    print(f"Image denoising time: {end_time - start_time:.4f} seconds", flush=True)

    return denoised

def denoise_image(image):
    """ Wrapper function to use fast_denoise. """
    return fast_denoise(image)
