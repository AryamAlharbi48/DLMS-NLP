from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .ocr_integration import perform_ocr

# -------------------------------
# قوائم الكلمات المرجعية
# -------------------------------
HIGH_KEYWORDS = [
    "ورثة", "إرث", "تقسيم التركة", "دين", "ديون", "مبلغ مستحق",
    "التزامات مالية", "قرض", "سداد دين", "أمانات", "فدية صيام",
    "زكاة فطرة", "قضاء", "كفارات"
]

MEDIUM_KEYWORDS = [
    "رقم هوية", "رقم الهوية الوطنية", "هوية وطنية", "بطاقة الهوية",
    "رقم السجل المدني", "بيانات الهوية", "إثبات هوية", "حساب بنكي",
    "رقم الحساب", "بطاقة بنكية", "بطاقة ائتمان", "بطاقة مصرفية",
    "بيانات الحساب", "كشف حساب", "رقم الآيبان", "IBAN", "تحويل بنكي",
    "وثيقة رسمية", "وثيقة قانونية", "عقد رسمي", "عقد بيع", "عقد إيجار",
    "اتفاقية", "إقرار قانوني", "تفويض رسمي", "توكيل شرعي",
    "وكالة شرعية", "صك ملكية", "رقم الصك", "العقار", "عقار",
    "ملكية عقار", "أرض", "قطعة أرض", "ملكية الأرض", "وصية",
    "وصية شرعية", "تركة مالية", "تركة عقارية"
]

LOW_KEYWORDS = [
    "فاتورة كهرباء", "فاتورة ماء", "فاتورة هاتف", "وصل استلام",
    "نموذج طلب", "تقرير شهري", "إيصال دفع", "شهادة حضور",
    "مراسلة بريدية", "مذكرة داخلية"
]

# -------------------------------
# تحميل الموديل (مرة واحدة فقط)
# -------------------------------
MODEL_NAME = "distilbert-base-multilingual-cased"
tokenizer = None
model = None

def load_model():
    global tokenizer, model
    if tokenizer is None or model is None:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModel.from_pretrained(MODEL_NAME)
        model.eval()

# -------------------------------
# دوال ML
# -------------------------------
def preprocess(text):
    return text.strip().lower() if text else ""

def get_embedding(text):
    load_model()
    text = preprocess(text)
    if not text:
        return np.zeros((1, 768))
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()

# دمج جميع الكلمات المرجعية
REFERENCE_TEXTS = HIGH_KEYWORDS + MEDIUM_KEYWORDS + LOW_KEYWORDS
load_model()
REFERENCE_EMBEDDINGS = np.vstack([get_embedding(t) for t in REFERENCE_TEXTS])

def classify_ml(text, threshold=0.85):
    """تصنيف النصوص باستخدام ML وCosine Similarity"""
    emb = get_embedding(text)
    similarities = cosine_similarity(emb, REFERENCE_EMBEDDINGS)
    max_idx = int(np.argmax(similarities))
    if similarities[0][max_idx] < threshold:
        return "Unclassified", float(similarities[0][max_idx])
    # تحديد الفئة حسب index
    if max_idx < len(HIGH_KEYWORDS):
        return "High", float(similarities[0][max_idx])
    elif max_idx < len(HIGH_KEYWORDS) + len(MEDIUM_KEYWORDS):
        return "Medium", float(similarities[0][max_idx])
    else:
        return "Low", float(similarities[0][max_idx])
