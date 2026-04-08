def evaluate_response(student_text: str):

    text = student_text.lower()

    score = {
        "treatment_approach": False,
        "modality": False,
        "safety": False,
        "objective": False
    }

    modality_label = "Unknown"

    # Treatment approach
    if any(x in text for x in ["cognitive behavioural", "cbt", "cbh", "solution focused", "ericksonian", "regression"]):
        score["treatment_approach"] = True

    # Modality
    if any(x in text for x in ["visual", "see", "image"]):
        score["modality"] = True
        modality_label = "Visual"
    elif any(x in text for x in ["hear", "sound", "auditory"]):
        score["modality"] = True
        modality_label = "Auditory"
    elif any(x in text for x in ["feel", "kinaesthetic", "pressure", "tense"]):
        score["modality"] = True
        modality_label = "Kinaesthetic"

    # Safety
    if any(x in text for x in ["risk", "safety", "medical", "history"]):
        score["safety"] = True

    # Objective
    if any(x in text for x in ["anxiety", "panic", "goal", "want to feel", "objective"]):
        score["objective"] = True

    total = sum(score.values())

    return {
        "scores": score,
        "total": total,
        "modality_label": modality_label
    }