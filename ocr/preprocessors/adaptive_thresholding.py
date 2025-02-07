import time
import cv2

def apply_adaptive_thresholding(image, method="gaussian"):
    start_time = time.time()
    """
    Applies adaptive thresholding to an image with method-specific parameters.

    Parameters:
        image (numpy.ndarray): Input image (already grayscale).
        method (str): "gaussian", "mean", or "trunc" for different thresholding methods.

    Returns:
        numpy.ndarray: Thresholded image.
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Set block size and C based on method
    if method == "mean":
        block_size, C = 15, 5  # Example: Higher block size for adaptive mean
        result = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, C
        )
    elif method == "gaussian":
        block_size, C = 11, 2  # Example: Smaller block size for gaussian
        result = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, C
        )
    elif method == "trunc":
        threshold_value = 127  # Set fixed threshold value for trunc
        _, result = cv2.threshold(image, threshold_value, 255, cv2.THRESH_TRUNC)
    else:
        raise ValueError(f"Invalid thresholding method: {method}")

    print(f'Adaptive thresholding ({method}) time: {time.time() - start_time:.4f} seconds')
    return result
