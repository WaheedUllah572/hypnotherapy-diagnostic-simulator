def evaluate_response(student_text: str):

    text = student_text.lower()

    score = {
        "treatment_approach": False,
        "modality": False,
        "safety": False,
        "objective": False
    }

    modality_label = "Unknown"

    # ----------- TREATMENT APPROACH (Q1) -----------
    if any(x in text for x in [
        "cognitive behavioural", "cbt", "cbh",
        "solution focused", "ericksonian", "regression"
    ]):
        score["treatment_approach"] = True

    # ----------- MODALITY (Q2) -----------
    if any(x in text for x in ["visual", "see", "image"]):
        score["modality"] = True
        modality_label = "Visual"

    elif any(x in text for x in ["hear", "sound", "auditory"]):
        score["modality"] = True
        modality_label = "Auditory"

    elif any(x in text for x in ["feel", "kinaesthetic", "pressure", "tense", "tight"]):
        score["modality"] = True
        modality_label = "Kinaesthetic"

    # ----------- OBJECTIVE (Q3) -----------
    if any(x in text for x in [
        "goal", "want", "reduce", "manage", "control",
        "improve", "cope", "anxiety", "panic"
    ]):
        score["objective"] = True

    # ----------- SAFETY (Q4) — STRICT -----------
    if any(x in text for x in [
        "risk", "safety", "medical", "history",
        "screen", "contraindication", "suitability"
    ]):
        score["safety"] = True

    total = sum(score.values())

    return {
        "scores": score,
        "total": total,
        "modality_label": modality_label
    }