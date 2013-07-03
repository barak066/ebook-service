
def generate_trigram(string, length=3):
    """
    Generates trigrams for string,
    like 'tipa' -> ['__t', '_ti', 'tip', 'ipa', 'pa_', 'a__']
    """
    lead_ = u'_' * (length - 1)
    string = lead_ + string + lead_
    trigrams = []
    for i in xrange(len(string) - length + 1):
        trigrams.append(string[i:i+length])
    return trigrams
        
