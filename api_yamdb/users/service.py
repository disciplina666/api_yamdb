def get_max_length(choices):
    return max(len(str(choice[0])) for choice in choices) if choices else 1