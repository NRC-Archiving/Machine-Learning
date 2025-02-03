import cv2

def denoise_image(image):
    return cv2.fastNlMeansDenoising(image, None, 30, 7, 21)
