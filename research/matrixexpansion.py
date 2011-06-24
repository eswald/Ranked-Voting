from itertools import combinations, count, permutations

class BallotFinder(object):
    r'''Finds a sample set of ballots for a given pairwise matrix.
        Not really intended for more general purpose constraint solving.
    '''#"""#'''
    
    def __init__(self, candidates):
        self.constraints = []
        
        perms = [str.join("", perm) for perm in permutations(c.lower() for c in candidates)]
        self.variables = dict.fromkeys(perms, 10)
        
        self.candidates = dict((c, [perm for perm in perms if perm.startswith(c.lower())]) for c in candidates)
        
        self.pairs = {}
        for a, b in combinations(candidates, 2):
            self.pairs[a+b] = [perm for perm in perms if perm.find(a.lower()) < perm.find(b.lower())]
            self.pairs[b+a] = [perm for perm in perms if perm.find(b.lower()) < perm.find(a.lower())]
    
    def check(self, varname):
        if varname in self.variables:
            return [varname]
        if varname in self.candidates:
            return self.candidates[varname]
        if varname in self.pairs:
            return self.pairs[varname]
        raise NameError(varname)
    
    def constrainGreater(self, greater, lesser):
        greater = self.check(greater)
        lesser = self.check(lesser)
        self.constraints.append((greater, lesser, True))
    
    def constrainEqual(self, first, second):
        first = self.check(first)
        second = self.check(second)
        self.constraints.append((first, second, False))
    
    def iterate(self, iteration):
        # Errors: negative contributions, positive contributions.
        # When sorted by value, variables too large should be at the head,
        # variables too small at the tail.
        errors = dict((key, [0, 0]) for key in self.variables)
        constraints = []
        total_errors = 0
        for left, right, greater in self.constraints:
            left_hand = sum(self.variables[name] for name in left)
            right_hand = sum(self.variables[name] for name in right)
            difference = left_hand - right_hand
            if greater:
                difference -= 1
                if difference >= 0:
                    left_bars = [0, difference]
                    right_bars = [0, -difference]
                    difference = 0
                else:
                    left_bars = [-difference, 0]
                    right_bars = [difference, 0]
            else:
                left_bars = [-difference, 0]
                right_bars = [difference, 0]
            total_errors += abs(difference)
            
            for name in left:
                errors[name][0] += left_bars[0]
                errors[name][1] += left_bars[1]
            for name in right:
                errors[name][0] += right_bars[0]
                errors[name][1] += right_bars[1]
            
            if difference:
                low, high = (left, right) if difference < 0 else (right, left)
                constraints.append((abs(difference), low, high))
        
        if not constraints:
            return True
        
        constraints.sort()
        fixer = constraints[-1]
        lows = sorted(fixer[1], key=errors.get)
        highs = sorted(fixer[2], key=errors.get)
        
        for item in highs:
            if self.variables[item] and item not in self.backsies:
                high = item
                break
        else:
            high = highs[0]
        
        for item in reversed(lows):
            if item not in self.backsies:
                low = item
                break
        else:
            low = lows[-1]
        
        self.backsies = [high, low]
        
        #for name in lows:
        #    print "Low:", name, self.variables[name], errors[name], name in self.backsies, name is low
        #for name in highs:
        #    print "High:", name, self.variables[name], errors[name], name in self.backsies, name is high
        print ("%d: %d; moving 1 from %s (%d: %d/%d) to %s (%d: %d/%d)" % (
                iteration, total_errors,
                high, self.variables[high], errors[high][0], errors[high][1],
                low, self.variables[low], errors[low][0], errors[low][1],
        ))
        
        self.variables[low] += 1
        if self.variables[high] >= 1:
            self.variables[high] -= 1
    
    def solve(self, statement, winner=None):
        for a, b in combinations(self.candidates, 2):
            ab = a + b
            ba = b + a
            
            if ab in statement and ba in statement:
                # The statement itself contains the ordering information.
                pass
            elif ab in statement:
                self.constrainGreater(ab, ba)
            elif ba in statement:
                self.constrainGreater(ba, ab)
            else:
                self.constrainEqual(ab, ba)
        
        prev = None
        for rank in statement.split(">"):
            pairs = rank.split("=")
            if prev:
                self.constrainGreater(prev, pairs[0])
            for n in range(len(pairs) - 1):
                self.constrainEqual(pairs[n], pairs[n+1])
            prev = pairs[-1]
        
        if winner:
            # Rig the election to have a specific winner
            for c in self.candidates:
                if c != winner:
                    self.constrainGreater(winner, c)
        
        self.backsies = []
        solved = False
        iteration = count(1)
        while not solved:
            solved = self.iterate(next(iteration))
        
        return self.variables
    
    def report(self):
        values = [
            ((-self.variables[name], name) for name in self.variables),
            ((-sum(self.variables[var] for var in self.pairs[name]), name) for name in self.pairs),
            ((-sum(self.variables[var] for var in self.candidates[name]), name) for name in self.candidates),
        ]
        
        for valueset in values:
            for value, name in sorted(valueset):
                print "%s = %s" % (name, -value)

def main(statement, winner=None):
    candidates = set(statement) - set("=>")
    if winner:
        assert winner in candidates
    solver = BallotFinder(candidates)
    solver.solve(statement, winner)
    solver.report()

if __name__ == "__main__":
    from sys import argv
    try:
        main(*argv[1:])
    except:
        print argv[0] + " 'AB>CD>BD=AD>BC>AC' [D]"
        raise
