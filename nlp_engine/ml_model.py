from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .ocr_integration import perform_ocr

# -------------------------------
#  ( اخف)Hugging Face موديل من DistilBERT غيرت المودل ل
# -------------------------------
MODEL_NAME = "distilbert-base-multilingual-cased"

tokenizer = None
model = None

def load_model():
    """Load tokenizer and model only once (lazy loading)."""
    global tokenizer, model
    if tokenizer is None or model is None:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModel.from_pretrained(MODEL_NAME)
        model.eval()


# -------------------------------
# دوال المعالجة
# -------------------------------
def preprocess(text):
    """Clean and normalize text."""
    if not text:
        return ""
    return text.strip().lower()


def get_embedding(text):
    """Return embedding vector for a given text."""
    load_model()  # 🔥 تأكد تحميل الموديل عند الحاجة فقط

    text = preprocess(text)
    if not text:
        return np.zeros((1, 768))

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)

    embeddings = outputs.last_hidden_state.mean(dim=1)

    return embeddings.numpy()


# -------------------------------
# بيانات مرجعية للنصوص الحساسة
# -------------------------------
REFERENCE_SENSITIVE_TEXTS = [
        "رقم هوية",
"رقم الهوية الوطنية",
"هوية وطنية",
"بطاقة الهوية",
"رقم السجل المدني",
"بيانات الهوية",
"إثبات هوية",
"حساب بنكي",
"رقم الحساب",
"بطاقة بنكية",
"بطاقة ائتمان",
"بطاقة مصرفية",
"بيانات الحساب",
"كشف حساب",
"رقم الآيبان",
"IBAN",
"تحويل بنكي",
"وثيقة رسمية",
"وثيقة قانونية",
"عقد رسمي",
"عقد بيع",
"عقد إيجار",
"اتفاقية",
"إقرار قانوني",
"تفويض رسمي",
"توكيل شرعي",
"وكالة شرعية",
"صك ملكية",
"رقم الصك",
"العقار",
"عقار",
"ملكية عقار",
"أرض",
"قطعة أرض",
"ملكية الأرض",
"وصية",
"وصية شرعية",
"تركة مالية",
"تركة عقارية",
"ورثة",
"إرث",
"تقسيم التركة",
"دين",
"ديون",
"مبلغ مستحق",
"التزامات مالية",
"قرض",
"سداد دين",
"أمانات",
"فدية صيام",
"زكاة فطرة",
"قضاء",
"كفارات",
]

# حساب الـ embeddings مرة واحدة فقط عند أول استخدام
load_model()
REFERENCE_EMBEDDINGS = np.vstack([get_embedding(text) for text in REFERENCE_SENSITIVE_TEXTS])


# -------------------------------
# دوال الـ ML لحساسية النصوص
# -------------------------------
def ml_score(text):
    """Compute maximum similarity score of text against sensitive references."""
    emb = get_embedding(text)
    similarities = cosine_similarity(emb, REFERENCE_EMBEDDINGS)
    max_score = float(np.max(similarities))
    return max_score


def is_sensitive_ml(text, threshold=0.65):
    """Return True if text is sensitive based on similarity threshold."""
    score = ml_score(text)
    return score >= threshold, score
