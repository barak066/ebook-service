"""Useful utilitys for words processing"""

def split_by_symbols(string, delimiters=[' ']):
    "Splits string by symbols in delimiters list"
    result = [string]

    # cplit by each delimiters
    for delimiter in delimiters:
        words = result
        result = []
        for word in words:
            result.extend(word.split(delimiter))

    # remove empty strings from result
    result = [word for word in result if word]

    return result



