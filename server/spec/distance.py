"Distance functions"

try:
    from itertools import permutations
except ImportError:
    def permutations(iterable, r=None):
        # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
        # permutations(range(3)) --> 012 021 102 120 201 210
        pool = tuple(iterable)
        n = len(pool)
#        r = n if r is None else r
        if r is None:
            r = n
        if r > n:
            return
        indices = range(n)
        cycles = range(n, n-r, -1)
        yield tuple(pool[i] for i in indices[:r])
        while n:
            for i in reversed(range(r)):
                cycles[i] -= 1
                if cycles[i] == 0:
                    indices[i:] = indices[i+1:] + indices[i:i+1]
                    cycles[i] = n - i
                else:
                    j = cycles[i]
                    indices[i], indices[-j] = indices[-j], indices[i]
                    yield tuple(pool[i] for i in indices[:r])
                    break
            else:
                return

def levenshtein_distance(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n
 
    current_row = range(n+1) # Keep current and previous row, not entire matrix
    for i in range(1, m+1):
        previous_row, current_row = current_row, [i]+[0]*m
        for j in range(1,n+1):
            add, delete = previous_row[j]+1, current_row[j-1]+1
            change = previous_row[j-1]
            if a[j-1] != b[i-1]:
                change += 1
            current_row[j] = min(add, delete, change)
 
    return current_row[n]


def name_distance(a, b):
    "Calculates minimal distance between two names"
    a, b = a.lower().split(), b.lower().split()

    if len(a) > len(b):
        a, b = b, a

    # calculating distance matrix
    m = []
    for a_word in a:
        m.append([])
        for b_word in b:
            m[-1].append( levenshtein_distance(a_word, b_word) )

    perms = permutations(range(len(b)), len(a))

    distances = []
    for perm in perms:
        
        d = 0
        for i in xrange(len(perm)):
            d += m[i][perm[i]]
        distances.append(d)

#    perms = permutations(range(len(b)), len(a))
#    for d in distances:
#        print perms.next()
#        print d
#        print



    return min(distances) + len(b) - len(a)

