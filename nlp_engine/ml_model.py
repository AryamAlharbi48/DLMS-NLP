from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from ocr_integration import perform_ocr

model_name = "bert-base-multilingual-cased"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

model.eval()   # مهم للإنتاج


def preprocess(text):

    if not text:
        return ""

    return text.strip().lower()



def get_embedding(text):

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




reference_sensitive_texts = [

    "رقم هوية",
    "وثيقة رسمية",
    "صك ملكية",
    "حساب بنكي",
    "بطاقة بنكية",
    "عقد رسمي"

]



# نحسبها مرة وحدة فقط
reference_embeddings = np.vstack(
    [get_embedding(text) for text in reference_sensitive_texts]
)



def ml_score(text):

    emb = get_embedding(text)

    similarities = cosine_similarity(emb, reference_embeddings)

    max_score = float(np.max(similarities))

    return max_score



def is_sensitive_ml(text, threshold=0.65):

    score = ml_score(text)

    if score >= threshold:
        return True, score
    else:
        return False, score