def evaluate_response(student_text: str):

    text = student_text.lower()

    score = {
        "treatment_approach": False,
        "modality": False,
        "safety": False,
        "objective": False
    }

    # Treatment approach
    if "cognitive behavioural" in text or "cbh" in text:
        score["treatment_approach"] = True
    if "solution focused" in text:
        score["treatment_approach"] = True
    if "ericksonian" in text:
        score["treatment_approach"] = True
    if "regression" in text:
        score["treatment_approach"] = True

    # Modality detection
    if "visual" in text or "see" in text:
        score["modality"] = True
    if "auditory" in text or "hear" in text:
        score["modality"] = True
    if "kinaesthetic" in text or "feel" in text:
        score["modality"] = True

    # Safety screening
    if "medical history" in text or "safety" in text or "risk" in text:
        score["safety"] = True

    # Client objective
    if "panic" in text or "anxiety" in text:
        score["objective"] = True

    total = sum(score.values())

    return {
        "scores": score,
        "total": total
    }