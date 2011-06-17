from itertools import combinations, permutations

candidates = "ABCD"

def well_sorted(ballot):
    for a, b in combinations(candidates[2:], 2):
        if (ballot.find(a) < ballot.find(b)) != (a < b):
            return False
    
    return True

def main():
    pairs = sorted(str.join("", sorted(pair)) for pair in combinations(candidates, 2))
    head = pairs.pop(0)
    length = len(pairs)
    
    count = 0
    for perm in permutations(pairs):
        for n in range(1 << length):
            tail = list(perm)
            for bit in range(length):
                if n & (1 << bit):
                    tail[-(bit+1)] = tail[-(bit+1)][::-1]
            
            tail.insert(0, head)
            ballot = str.join(">", tail)
            if not well_sorted(ballot):
                continue
            
            print ballot
            count += 1
    
    print count

if __name__ == "__main__":
    main()
