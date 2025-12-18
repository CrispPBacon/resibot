import cv2
import numpy as np


def image_pre_process(img):
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted_img = cv2.bitwise_not(gray_image)
    return inverted_img


def crop_white_content_area(image):
    """
    Detects and crops the largest white area in the input image.

    Parameters:
        image (str or np.ndarray): Path to image file or loaded BGR image as NumPy array.

    Returns:
        cropped (np.ndarray): Cropped image containing the largest white area.
                             Returns None if no white area found.
        bbox (tuple): Bounding box (x, y, w, h) of the cropped area.
                      None if no white area found.
    """
    # Load image if a path is provided
    if isinstance(image, str):
        img = cv2.imread(image)
        if img is None:
            raise FileNotFoundError(f"Image not found at path: {image}")
    else:
        img = image.copy()

    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define white color range in HSV
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])

    # Threshold to get white regions
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Morphological closing to clean mask
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Find contours
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, None  # No white area found

    # Find largest contour by area
    largest_contour = max(contours, key=cv2.contourArea)

    # Get bounding box of largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Crop and return the white content area
    height = (y+h-25) - (y+50)
    cropped = img[y+(h//12):(y+h)-25, x:x+w]

    # cv2.imwrite(f'output/{image.split("/")[1].split(".")[0]}.png', cropped)
    # return cropped, (x, y, w, h)
    return cropped


def remove_gcash_footer(img):
    h, w = img.shape[:2]

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Edge detection to capture rounded-rectangle outline
    edges = cv2.Canny(gray, 30, 120)

    # Only search bottom half of the image
    bottom_half = edges[int(h * 0.45):, :]

    contours, _ = cv2.findContours(
        bottom_half, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    footer_y = None
    footer_h = None

    for cnt in contours:
        x, y, w2, h2 = cv2.boundingRect(cnt)

        # Skip small objects
        if h2 < 60 or w2 < w * 0.6:
            continue

        # Convert contour y to original image coordinate
        real_y = int(h * 0.45) + y

        # Choose the LOWEST large rectangle → the gray footer
        if footer_y is None or real_y > footer_y:
            footer_y = real_y
            footer_h = h2

    # If no footer detected → return original
    if footer_y is None:
        return img

    # Crop everything ABOVE the footer
    cleaned = img[:footer_y, :]
    return cleaned
