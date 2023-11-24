def evaluate_json(json_file):
    import json
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data