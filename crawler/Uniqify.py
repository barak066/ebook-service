#!/usr/bin/python

def uniqify_nop( sequence ):    # Not order preserving
    return {}.fromkeys(sequence).keys()


def uniqify_op( sequence ):    # Order preserving
    seen = set()
    return [x for x in sequence if x not in seen and not seen.add(x)]


def uniqify_op_transform( sequence, transformFunction = None ):   # Order preserving
    if transformFunction is None:
        def transformFunction(x): return x
    seen = {}
    result = []
    for item in sequence:
        marker = transformFunction(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result
