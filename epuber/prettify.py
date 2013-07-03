"""
Functions to make pretty texts.
"""
import re

def remove_spaces(text):
    """
    Removes spaces before full stops, commas, question marks,
    exclamation marks, semicolons, colons.
    """
    out = text[:]
    regex = re.compile(r" ([\.,\?\!;:])")
    match = regex.search(out)
    while match:
        out = out[:match.start()] + match.group(1) + out[match.end():]
        match = regex.search(out)

    out = re.sub("&nbsp;", "&#160;", out)

    return out

def remove_unnecessary_tags(text):
    """
    Removes </i><i> and </b><b>
    """
    out = text[:]
    regex = re.compile(r"</([ib])>\s*<\1>")
    match = regex.search(out)
    while match:
        out = out[:match.start()] + out[match.end():]
        match = regex.search(out)

    return out

