# -*- coding: utf-8 -*-

def recommend(genres1, genres2):
    likeness = 0.0
    probs = {}
    weights = {}
    for g in genres1.keys() + genres2.keys():
        gg1 = genres1.get(g, 0)
        gg2 = genres2.get(g, 0)
        if gg1 >= 0.0 and gg2 >= 0.0 and gg1 < 0.05 and gg2 < 0.05:
            weights[g] = 0
            probs[g] = 0.5
        else:
            if gg1 < 0 or gg2 < 0:
                return -1
            else:
                if gg1 > gg2:
                    probs[g] = gg2 / gg1
                    weights[g] = gg1**2
                else:
                    probs[g] = gg1 / gg2
                    weights[g] = gg2**2
    sumprobs = 0.0
    sumweights = 0.0
    for g in probs:
        sumprobs += probs[g] * weights[g]
        sumweights += weights[g]
    if sumweights == 0:
        return 0
    likeness = sumprobs / sumweights
    return likeness
