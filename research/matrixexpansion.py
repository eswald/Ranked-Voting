from itertools import combinations, count, permutations

from voting.methods import methods

class Sum(dict):
    def __init__(self, namespace, items = {}):
        self.counts = dict.fromkeys(items, 1)
        self.values = namespace
    
    def __call__(self):
        return sum(self.values[name] * self.counts[name] for name in self.counts)
    
    def __iter__(self):
        for name in self.counts:
            yield name
    
    def __str__(self):
        return " + ".join(name if self.counts[name] == 1 else "%d*%s" % (self.counts[name], name) for name in sorted(self))
    
    def __sub__(self, other):
        result = self.__class__(self.values)
        for name in self.counts:
            count = self.counts[name] - other.counts.get(name, 0)
            if count > 0:
                result.counts[name] = count
        return result
    
    def __setitem__(self, name, value):
        self.counts[name] = value
    
    def __nonzero__(self):
        return any(self.counts.values())
            

class BallotFinder(object):
    r'''Finds a sample set of ballots for a given pairwise matrix.
        Not really intended for more general purpose constraint solving.
    '''#"""#'''
    
    def __init__(self, candidates):
        self.constraints = []
        
        perms = [str.join("", perm) for perm in permutations(c.lower() for c in candidates)]
        self.variables = dict.fromkeys(perms, 10)
        
        self.candidates = dict((c, Sum(self.variables, (perm for perm in perms if perm.startswith(c.lower())))) for c in candidates)
        
        self.pairs = {}
        for a, b in combinations(candidates, 2):
            self.pairs[a+b] = Sum(self.variables, (perm for perm in perms if perm.find(a.lower()) < perm.find(b.lower())))
            self.pairs[b+a] = Sum(self.variables, (perm for perm in perms if perm.find(b.lower()) < perm.find(a.lower())))
        
        self.bordas = dict((c, Sum(self.variables)) for c in candidates)
        last = len(candidates) - 1
        for perm in perms:
            for pos, char in enumerate(perm):
                self.bordas[char.upper()][perm] = last - 2*pos
    
    def check(self, varname):
        if varname.startswith("Borda-"):
            return self.bordas[varname[6:]]
        if varname in self.variables:
            return Sum([varname])
        if varname in self.candidates:
            return self.candidates[varname]
        if varname in self.pairs:
            return self.pairs[varname]
        raise NameError(varname)
    
    def constrainGreater(self, greater, lesser):
        bigger = self.check(greater)
        smaller = self.check(lesser)
        bigger, smaller = bigger - smaller, smaller - bigger
        if bigger or smaller:
            print "%s > %s: %s > %s" % (greater, lesser, bigger, smaller)
            self.constraints.append((bigger, smaller, True))
        else:
            # A given set of variables cannot be greater than itself.
            raise ValueError("Unsatisfiable constraint")
    
    def constrainEqual(self, left, right):
        first = self.check(left)
        second = self.check(right)
        first, second = first - second, second - first
        if first or second:
            print "%s = %s: %s = %s" % (left, right, first, second)
            self.constraints.append((first, second, False))
    
    def iterate(self, iteration):
        # Errors: negative contributions, positive contributions.
        # When sorted by value, variables too large should be at the head,
        # variables too small at the tail.
        errors = dict((key, [0, 0]) for key in self.variables)
        constraints = []
        total_errors = 0
        for left, right, greater in self.constraints:
            difference = left() - right()
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
    
    def setup(self, statement):
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
    
    def plurality(self, winner):
        # Rig the election to have a specific winner
        for c in self.candidates:
            if c != winner:
                self.constrainGreater(winner, c)
    
    def borda(self, winner):
        # Rig the election to have a specific winner
        for c in self.candidates:
            if c != winner:
                self.constrainGreater("Borda-"+winner, "Borda-"+c)
    
    def solve(self):
        self.backsies = []
        solved = False
        iteration = count(1)
        while not solved:
            solved = self.iterate(next(iteration))
        
        return self.variables
    
    def report(self):
        values = [
            ((-self.variables[name], name) for name in self.variables),
            ((-self.pairs[name](), name) for name in self.pairs),
            ((-self.candidates[name](), name) for name in self.candidates),
            ((-self.bordas[name](), "Borda-"+name) for name in self.bordas),
        ]
        
        for valueset in values:
            for value, name in sorted(valueset):
                print "%s = %s" % (name, -value)
        
        for method in methods:
            ballots = [(key.upper(), self.variables[key]) for key in self.variables]
            result = methods[method](ballots, set(self.candidates))
            rewritten = " > ".join("=".join(sorted(r)) for r in result)
            print "%-8s\t%s" % (method+":", rewritten)

def main(statement, winner=None):
    candidates = set(statement) - set("=>")
    if winner:
        assert winner in candidates
    solver = BallotFinder(candidates)
    solver.setup(statement)
    if winner:
        #solver.plurality(winner)
        solver.borda(winner)
    solver.solve()
    solver.report()

if __name__ == "__main__":
    from sys import argv
    try:
        main(*argv[1:])
    except:
        print argv[0] + " 'AB>CD>BD=AD>BC>AC' [D]"
        raise
