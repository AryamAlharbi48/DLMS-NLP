import sys
import os

# Add root folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp_engine.ml_model import process_image_with_ocr_and_ml
from nlp_engine.rule_based import process_image_with_ocr_and_rules

def main():
    test_image_path = os.path.abspath("../test_image.txt")

    print("\n--- Testing ML ---")
    print(process_image_with_ocr_and_ml(test_image_path))

    print("\n--- Testing Rule-Based ---")
    print(process_image_with_ocr_and_rules(test_image_path))

if __name__ == "__main__":
    main()
    