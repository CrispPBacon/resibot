from .parser import hybrid_parse_gcash_receipt
from .ocr import extract_text
from .image_process import image_pre_process, remove_gcash_footer, crop_white_content_area
import cv2


def process_receipt_image(image_path):
    image = crop_white_content_area(image_path)
    footer_cropped_image = remove_gcash_footer(image)
    processed_image = image_pre_process(footer_cropped_image)
    raw_text = extract_text(processed_image)

    # ====== Save the image for viewing. (Optional) ======
    path = image_path.split(".")[0] + "_output.png"
    cv2.imwrite(path, processed_image)

    # ====== OCR Processing Method ======
    # result = parse_receipt(raw_text) # Pure openai parse, TAKES ATLEAST 3 SECONDS.
    # result = regex_parse_receipt(raw_text) # FAST but sometimes inaccurate.

    # Takes advantage of both openai and regex.
    result = hybrid_parse_gcash_receipt(raw_text)
    return result
