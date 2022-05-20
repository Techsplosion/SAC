def filter_list(condition, list):
    return [x for x in list if condition(x)]