import cv2
import time

def upscale_image(image, scale_factor=2):
    start_time = time.time()  # Start time tracking

    width = int(image.shape[1] * scale_factor)
    height = int(image.shape[0] * scale_factor)
    dim = (width, height)

    upscaled = cv2.resize(image, dim, interpolation=cv2.INTER_CUBIC)

    end_time = time.time()  # End time tracking
    print(f"Time elapsed in upscaling.py: {end_time - start_time:.4f} seconds")

    return upscaled
