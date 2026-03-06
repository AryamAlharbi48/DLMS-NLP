from django.test import TestCase
from ml_model import ml_score
from rule_based import is_sensitive
from hybrid import final_classification

from sklearn.metrics import classification_report
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import os


class SensitivityTestCase(TestCase):

    def test_files_classification(self):

        # -----------------------------
        # ملفات (صور + PDF + TXT)
        # -----------------------------
        test_files = [
            "id_card.jpg",
            "contract.jpg",
            "document.jpg",
            "bank.pdf",
            "notes.txt"
        ]

        #real classification for files must be enterd 
        y_true = [
            "HIGH",
            "HIGH",
            "LOW",
            "HIGH",
            "LOW"
        ]

        # -----------------------------
        # قوائم التوقعات
        # -----------------------------
        y_pred_ml = []
        y_pred_rule = []
        y_pred_hybrid = []

        # -----------------------------
        # OCR for extraxting the text from the pic
        # -----------------------------
        def extract_text_from_image(image_path):
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang="ara")
            return text.strip()

        # -----------------------------
        # OCR for extraxting the text from the PDF
        # -----------------------------
        def extract_text_from_pdf(pdf_path):
            text = ""
            images = convert_from_path(pdf_path)
            for img in images:
                page_text = pytesseract.image_to_string(img, lang="ara")
                text += page_text + " "
            return text.strip()

        # -----------------------------
        # reading text file
        # -----------------------------
        def extract_text_from_txt(txt_path):
            with open(txt_path, "r", encoding="utf-8") as file:
                return file.read().strip()

        # -----------------------------
        # function for specifying the type of the enterd files 
        # -----------------------------
        def extract_text(file_path):
            extension = os.path.splitext(file_path)[1].lower()

            if extension == ".pdf":
                return extract_text_from_pdf(file_path)

            elif extension == ".txt":
                return extract_text_from_txt(file_path)

            else:
                return extract_text_from_image(file_path)

        # -----------------------------
        # analyze every file
        # -----------------------------
        for file_path in test_files:

            # OCR
            text = extract_text(file_path)

            print("Extracted Text:", text)

            # -------- ML --------
            score_ml = ml_score(text)
            # تعديل 3 مستويات
            if score_ml > 0.6:
                level_ml = "HIGH"
            elif score_ml > 0.3:
                level_ml = "MEDIUM"
            else:
                level_ml = "LOW"
            y_pred_ml.append(level_ml)

            # ----- Rule Based -----
            sensitive, score_rule = is_sensitive(text)
            #  3 مستويات
            if score_rule > 0.6:
                level_rule = "HIGH"
            elif score_rule > 0.3:
                level_rule = "MEDIUM"
            else:
                level_rule = "LOW"
            y_pred_rule.append(level_rule)

            # ------- Hybrid -------
            hybrid_result = final_classification(text)
            level_hybrid = hybrid_result["level"].upper()
            y_pred_hybrid.append(level_hybrid)

        # -----------------------------
        #  Precision / Recall / F1
        # -----------------------------
        labels = ["LOW", "MEDIUM", "HIGH"]

        print("\n===== ML Report =====")
        print(classification_report(y_true, y_pred_ml, labels=labels))

        print("\n===== Rule Based Report =====")
        print(classification_report(y_true, y_pred_rule, labels=labels))

        print("\n===== Hybrid Report =====")
        print(classification_report(y_true, y_pred_hybrid, labels=labels))
