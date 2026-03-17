from rapidfuzz import fuzz
from nlp_engine.ocr_integration import perform_ocr


SENSITIVE_KEYWORDS = [
     
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

THRESHOLD = 0.60   #  بنفس مقياس النتيجة النهائية


def preprocess(text):
    if not text:
        return ""
    return text.strip().lower()


def fuzzy_match_score(text):

    text = preprocess(text)

    if not text:
        return 0.0

    max_score = 0

    for keyword in SENSITIVE_KEYWORDS:

        similarity = fuzz.partial_ratio(keyword, text)

        # boost إذا الكلمة موجودة حرفياً
        if keyword in text:
            similarity += 20

        similarity = min(similarity, 100)

        if similarity > max_score:
            max_score = similarity

    final_score = max_score / 100

    return final_score


def is_sensitive(text):

    score = fuzzy_match_score(text)

    if score >= THRESHOLD:
        return True, score
    else:
        return False, score