from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from nlp_engine.ocr_integration import perform_ocr

model_name = "bert-base-multilingual-cased"

# Lazy loading — model only loads when first needed, not at Django startup
_tokenizer = None
_model = None
_reference_embeddings = None

def get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
    return _tokenizer

def get_model():
    global _model
    if _model is None:
        _model = AutoModel.from_pretrained(model_name)
        _model.eval()
    return _model

def preprocess(text):
    if not text:
        return ""
    return text.strip().lower()

def get_embedding(text):
    text = preprocess(text)
    if not text:
        return np.zeros((1, 768))
    tokenizer = get_tokenizer()
    model = get_model()
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

reference_sensitive_texts = [
      
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

def get_reference_embeddings():
    global _reference_embeddings
    if _reference_embeddings is None:
        _reference_embeddings = np.vstack(
            [get_embedding(text) for text in reference_sensitive_texts]
        )
    return _reference_embeddings

def ml_score(text):
    emb = get_embedding(text)
    similarities = cosine_similarity(emb, get_reference_embeddings())
    max_score = float(np.max(similarities))
    return max_score

def is_sensitive_ml(text, threshold=0.65):
    score = ml_score(text)
    if score >= threshold:
        return True, score
    else:
        return False, score