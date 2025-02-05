import cv2
import numpy as np
import time

def deskew_image(image, angle_threshold=1.5):
    """
    Deskews an image only if the skew angle is significant.
    - Skips deskewing if the angle is small (≤ angle_threshold degrees).
    - Saves processing time for already aligned pages.
    """

    start_time = time.time()  # Start time tracking

    # Ensure image is grayscale
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]

    # Normalize angle
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # ✅ Skip deskewing if the angle is small
    if abs(angle) <= angle_threshold:
        print(f"Skipping deskewing (angle {angle:.2f}° is within threshold)", flush=True)
        return image

    # Apply rotation
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    end_time = time.time()  # End time tracking
    print(f"Deskewing time: {end_time - start_time:.4f} seconds")

    return rotated
