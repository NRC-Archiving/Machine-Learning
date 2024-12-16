from PIL import Image

def crop_image_body(image_path: str, output_path: str, crop_ratio: float = 0.2):
    """
    Crop the body of an image by excluding the top portion (letterhead).

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the cropped image.
        crop_ratio (float): Ratio of the image height to crop from the top. Default is 20% (0.2).
    
    Returns:
        None
    """
    try:
        image = Image.open(image_path)
        width, height = image.size
        crop_area = (0, int(height * crop_ratio), width, height)
        cropped_image = image.crop(crop_area)
        cropped_image.save(output_path)
        print(f"Cropped body saved to {output_path}")
    except Exception as e:
        print(f"Error cropping image: {e}")
