import time
import cv2

def apply_adaptive_thresholding(image, method="gaussian", block_size=11, C=2):
    start_time = time.time()
    """
    Applies adaptive thresholding to an image.

    Parameters:
        image (numpy.ndarray): Input image (already grayscale).
        method (str): "gaussian" or "mean" for different adaptive methods.
        block_size (int): Size of the pixel neighborhood (must be odd).
        C (int): Constant subtracted from the mean or weighted sum.

    Returns:
        numpy.ndarray: Thresholded image.
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if method == "mean":
        result = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, C
        )
    elif method == "gaussian":
        result = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, C
        )
    else:
        raise ValueError(f"Invalid thresholding method: {method}")

    print(f'Adaptive tresholding time: {time.time() - start_time:.4f} seconds')
    return result
