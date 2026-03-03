import os

def perform_ocr(image_path):
    """
    Placeholder OCR function.
    Reads text file content (temporary fake OCR).
    """
    try:
        with open(image_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print("OCR Error:", e)
        return None