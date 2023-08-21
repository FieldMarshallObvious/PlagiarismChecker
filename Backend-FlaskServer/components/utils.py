from components.PreProcess_Text import extract_keywords

def check_request_data(data, required_fields):
    if not data:
        return "Invalid data", 400

    for key, expected_type in required_fields.items():
        if key not in data:
            return f"Missing {key}", 400
        if not isinstance(data[key], expected_type):
            return f"{key} is not of type {expected_type.__name__}", 400
        if expected_type == list and not data[key]:
            return f"{key} is empty", 400

    return None

def extract_keywords_from_text(data):
    text = data['text']
    results = extract_keywords(text)
    return {"results": results}