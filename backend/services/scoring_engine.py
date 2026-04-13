def evaluate_response(student_text: str, mode: str):

    text = student_text.lower()

    if mode == "approach":
        return any(x in text for x in [
            "cognitive behavioural", "cbt", "cbh",
            "solution focused", "ericksonian", "regression"
        ])

    if mode == "modality":
        return any(x in text for x in [
            "visual", "auditory", "kinaesthetic", "feel", "see", "hear"
        ])

    if mode == "objective":
        return any(x in text for x in [
            "want", "goal", "reduce", "manage", "control", "cope"
        ])

    if mode == "safety":
        return any(x in text for x in [
            "risk", "safety", "medical", "history", "screen", "suitability"
        ])

    return False