
def check_threshold(current_level, limit=3):
    if current_level >= limit:
        return True
    return False