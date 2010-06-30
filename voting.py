from collections import defaultdict

def _maybe_tuple(items):
    if len(items) == 1:
        return items[0]
    else:
        return tuple(items)

def rankedpairs(prefs):
    pass

def instantrunoff(prefs):
    pass

def plurality(prefs):
    # First past the post, winner takes all.
    # Only the top preference is even looked at.
    totals = defaultdict(int)
    for ranks, count in prefs:
        totals[ranks[0]] += count
        
        # Ensure that the other candidates make it into the result.
        for candidate in ranks[1:]:
            totals[candidate] += 0
    
    counts = defaultdict(list)
    for key in totals:
        counts[totals[key]].append(key)
    
    result = sorted(counts)
    result.reverse()
    return [_maybe_tuple(counts[total]) for total in result]

def borda(prefs):
    pass

def bucklin(prefs):
    pass

def minimax(prefs):
    pass

def schulze(prefs):
    pass

def kemeny(prefs):
    pass
