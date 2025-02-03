import cv2
import numpy as np

def crop_letterhead(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_height = 0
    header_bottom = 0

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if y < image.shape[0] * 0.25:
            if h > max_height:
                max_height = h
                header_bottom = y + h

    if header_bottom > 50:
        return image[header_bottom:, :]
    else:
        return image
