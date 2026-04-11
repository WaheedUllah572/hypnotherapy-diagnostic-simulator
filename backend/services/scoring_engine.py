def evaluate_response(student_text: str):

    # 🔥 IMPORTANT: expect structured input (q1–q4 combined text fallback safe)
    text = student_text.lower()

    score = {
        "treatment_approach": False,
        "modality": False,
        "safety": False,
        "objective": False
    }

    modality_label = "Unknown"

    # ----------- IMPROVED LOGIC (ALIGNED BETTER) -----------

    # Treatment approach (Q1)
    if any(x in text for x in [
        "cognitive behavioural", "cbt", "cbh",
        "solution focused", "ericksonian", "regression"
    ]):
        score["treatment_approach"] = True

    # Modality (Q2)
    if any(x in text for x in ["visual", "see", "image"]):
        score["modality"] = True
        modality_label = "Visual"
    elif any(x in text for x in ["hear", "sound", "auditory"]):
        score["modality"] = True
        modality_label = "Auditory"
    elif any(x in text for x in ["feel", "kinaesthetic", "pressure", "tense"]):
        score["modality"] = True
        modality_label = "Kinaesthetic"

    # Objective (Q3)
    if any(x in text for x in [
        "goal", "want", "reduce", "manage", "control",
        "anxiety", "panic"
    ]):
        score["objective"] = True

    # Safety (Q4)  ✅ IMPROVED
    if any(x in text for x in [
        "risk", "safety", "medical", "history",
        "screen", "contraindication"
    ]):
        score["safety"] = True

    total = sum(score.values())

    return {
        "scores": score,
        "total": total,
        "modality_label": modality_label
    }