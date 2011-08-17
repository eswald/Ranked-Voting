from itertools import combinations, permutations

from voting.util import interleave

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

def with_equality():
    for matrix in fully_ranked():
        length = len(matrix) - 1
        ordered = 0
        for pair in reversed(matrix):
            if pair[0] > pair[1]:
                break
            ordered += 1
        
        for n in range(1 << length):
            signs = []
            for bit in range(length):
                if n & (1 << bit):
                    if matrix[-(bit+1)] < matrix[-(bit+2)]:
                        break
                    signs.insert(0, "=")
                else:
                    signs.insert(0, ">")
            
            if len(signs) == length:
                result = str.join("", interleave(matrix, signs))
                yield result
                
                tied = 1
                while signs and signs.pop() == "=":
                    tied += 1
                if tied <= ordered:
                    yield result + "=" + (result[-1:result.rfind(">"):-1] or result[::-1])

def main():
    count = 0
    for ballot in with_equality():
        print ballot
        count += 1
    
    print count

if __name__ == "__main__":
    main()
