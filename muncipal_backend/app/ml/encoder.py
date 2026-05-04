ISSUE_TYPE_MAPPING = {
    'drainage': 0,
    'garbage': 1,
    'graffiti': 2,
    'illegal_dumping': 3,
    'illegal_parking': 4,
    'noise': 5,
    'other': 6,
    'pothole': 7,
    'streetlight': 8,
    'water_leakage': 9
}

def encode_issue_type(issue_type: str) -> int:
    return ISSUE_TYPE_MAPPING.get(issue_type, 6)  # default to 'other' if unknown