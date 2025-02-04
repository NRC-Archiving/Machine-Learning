import cv2
import numpy as np
import time

def remove_background(image, k=2):
    """
    Removes colored background while preserving text.

    Parameters:
        image (numpy.ndarray): Input image (colored).
        k (int): Number of clusters for K-means (2 for background & text separation).

    Returns:
        numpy.ndarray: Image with background removed.
    """
    start_time = time.time()

    # Convert to LAB color space for better separation
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)

    # Apply K-means clustering to detect background color
    pixel_values = image.reshape((-1, 3))
    pixel_values = np.float32(pixel_values)

    # Define K-means criteria & apply clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert centers to integer values
    centers = np.uint8(centers)
    labels = labels.flatten()

    # Assign segmented colors back to image
    segmented_image = centers[labels].reshape(image.shape)

    # Convert to grayscale while preserving text contrast
    gray = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2GRAY)
    
    print(f'Background removal time: {time.time() - start_time:.4f} seconds')
    return gray
