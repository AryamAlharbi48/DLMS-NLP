from .rule_based import fuzzy_match_score
from .ml_model import ml_score


FUZZY_WEIGHT = 0.6
ML_WEIGHT = 0.4


def preprocess(text):

    return text.strip().lower()


def final_classification(text):

    text = preprocess(text)

    fuzzy = fuzzy_match_score(text)

    try:
        ml = ml_score(text)
    except:
        ml = 0


    final_score = (FUZZY_WEIGHT * fuzzy) + (ML_WEIGHT * ml)


    if final_score > 0.6:

        level = "HIGH"

    elif final_score > 0.3:

        level = "MEDIUM"

    else:

        level = "LOW"


    return {

        "fuzzy_score": fuzzy,

        "ml_score": ml,

        "final_score": final_score,

        "level": level

    }