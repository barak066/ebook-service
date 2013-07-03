def soundex(name, len=4):

    # digits holds the soundex values for the alphabet
    digits = '01230120022455012623010202'
    sndx = ''
    fc = ''

    # translate alpha chars in name to soundex digits
    for c in name.upper():
        if c.isalpha():
            if not fc: fc = c   # remember first letter

            try:
                d = digits[ord(c)-ord('A')]
            except IndexError:
                # if char is out of range, then ignore this char
                d = '0'
            
            # duplicate consecutive soundex digits are skipped
            if not sndx or (d != sndx[-1]):
                sndx += d
    
    sndx = fc + sndx[1:]   # replace first digit with first char
    sndx = sndx.replace('0','')       # remove all 0s
    return (sndx + (len * '0'))[:len] # padded to len characters
