import pytesseract


def extract_text(image):
    text = pytesseract.image_to_string(
        image,
        config=r"--oem 3 --psm 6"
    )

    lines = text.split("\n")
    lines[0] = mask_name_style(lines[0])
    result = "\n".join(lines)

    return result


def mask_name_style(text):
    """
    Processes better name value | e.g name: JO*N PA*L L.
    Keep only uppercase letters, spaces, and periods.
    Replace everything else with bullet '•'.
    """
    return "".join([c if c.isupper() or c == " " or c == "." else "•" for c in text])
