def soundex(name, len=4):
    """Creates soundex code for word"""

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


def soundex_for_string(string, length=4):
    """Create soundex codes for each words in string"""
    words = string.split()

    words = [soundex(word, length) for word in words]

    return ' '.join(words)


def prepare_query(query):
    """Prepares query for send to search engine.
    Replaces '-' to ' '"""
    # TODO replace letters with diacritical sign to letters without its
    return query.replace('-', ' ')



def sphinx_weight_cmp(x, y):
    "Compares x and y using sphinx weights."
    return -1 * cmp(x.sphinx['weight'], y.sphinx['weight'])


def join_query_list(first, second, comparator=sphinx_weight_cmp):
    """Joins two lists of query sets, sorts by weight,
    makes unique elements by id.
    Default comparator is sphinx_weight_cmp."""

    items = []
    items.extend(first)
    items.extend(second)
    items.sort(comparator)

    item_set = set()
    result = []

    # make unique with saving ordering
    for item in items:
        if not (item.id in item_set):
            # if id is not in set, than add it to set, and add item to result
            item_set.add(item.id)
            result.append(item)

    return result


def rm_items(items, id_set, id_f):
    """Returns new item list.
    Removes item from items, if id_f(item) is in id_set."""

    result = []

    for item in items:
        if id_f(item) not in id_set:
            result.append(item)

    return result
            

def id_field(entity):
    "Returns entity.id"
    return entity.id
