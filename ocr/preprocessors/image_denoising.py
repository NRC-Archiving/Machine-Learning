import cv2
import time
import sys  # ✅ Needed to force print in multiprocessing

def fast_denoise(image, downscale_factor=3):
    """
    Optimized denoising function:
    - Downscales image before denoising (faster processing).
    - Uses tuned parameters for faster execution.
    - Upscales back to retain OCR accuracy.
    """

    start_time = time.time()

    # Step 1: Downscale image
    height, width = image.shape[:2]
    small_image = cv2.resize(image, (width // downscale_factor, height // downscale_factor), interpolation=cv2.INTER_LINEAR)

    # Step 2: Apply faster denoising
    denoised_small = cv2.fastNlMeansDenoising(small_image, None, h=7, templateWindowSize=5, searchWindowSize=15)

    # Step 3: Upscale back to original size
    denoised = cv2.resize(denoised_small, (width, height), interpolation=cv2.INTER_LINEAR)

    end_time = time.time()
    
    # ✅ Force print in multi-processing
    print(f"Time elapsed in fast_denoise: {end_time - start_time:.4f} seconds", flush=True)
    sys.stdout.flush()  # ✅ Ensure print works even in multi-processing

    return denoised


def denoise_image(image):
    """ Wrapper to use fast_denoise instead of standard OpenCV denoising. """
    return fast_denoise(image)
