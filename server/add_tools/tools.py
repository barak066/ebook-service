def smart_split(string_list, split_params):
    if not split_params:
        return string_list

    splitted_string = []
    for string in string_list:
        splitted_string.extend(string.split(split_params[0]))
    return smart_split(splitted_string, split_params[1:])
