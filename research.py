from itertools import combinations, permutations

candidates = "ABCD"

def well_sorted(ballot):
    ballot = str.join("", ballot)
    for a, b in combinations(candidates[2:], 2):
        if (ballot.find(a) < ballot.find(b)) != (a < b):
            return False
    
    return True

def fully_ranked():
    pairs = sorted(str.join("", sorted(pair)) for pair in combinations(candidates, 2))
    head = pairs.pop(0)
    length = len(pairs)
    
    for perm in permutations(pairs):
        for n in range(1 << length):
            tail = list(perm)
            for bit in range(length):
                if n & (1 << bit):
                    tail[-(bit+1)] = tail[-(bit+1)][::-1]
            
            tail.insert(0, head)
            if not well_sorted(tail):
                continue
            
            yield tail

def main():
    count = 0
    for ballot in fully_ranked():
        print str.join(">", ballot)
        count += 1
    
    print count

if __name__ == "__main__":
    main()
