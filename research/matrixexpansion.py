from itertools import combinations, count, permutations

# sudo apt-get install glpk python-glpk
# pip install pulp
from pulp import COIN, LpVariable, LpProblem, LpMinimize, LpStatus, value as LpValue

from voting.methods import methods

class Sum(dict):
    def __init__(self, namespace, items = {}):
        self.counts = dict.fromkeys(items, 1)
        self.values = namespace
    
    def __call__(self):
        return sum(LpValue(self.values[name]) * self.counts[name] for name in self.counts)
    
    def __iter__(self):
        for name in self.counts:
            yield name
    
    def __str__(self):
        return " + ".join(name if self.counts[name] == 1 else "%d*%s" % (self.counts[name], name) for name in sorted(self))
    
    def __sub__(self, other):
        result = self.__class__(self.values)
        for name in set(self.counts.keys() + other.counts.keys()):
            count = self.counts.get(name, 0) - other.counts.get(name, 0)
            if count != 0:
                result.counts[name] = count
        return result
    
    def __setitem__(self, name, value):
        self.counts[name] = value
    
    def __nonzero__(self):
        return any(self.counts.values())
    
    def sum(self):
        return sum(self.counts[name] * self.values[name] for name in self.counts)
    
    def __gt__(self, other):
        return (self - other).sum() >= 1
    
    def __eq__(self, other):
        return self.sum() == other.sum()

class BallotFinder(object):
    r'''Finds a sample set of ballots for a given pairwise matrix.
        Not really intended for more general purpose constraint solving.
    '''#"""#'''
    
    def __init__(self, candidates):
        perms = [str.join("", perm) for perm in permutations(c.lower() for c in candidates)]
        self.variables = dict((name, LpVariable(name, 0, cat="Integer")) for name in perms)
        self.total = Sum(self.variables, perms)
        
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
            return Sum(self.variables, [varname])
        if varname in self.candidates:
            return self.candidates[varname]
        if varname in self.pairs:
            return self.pairs[varname]
        raise NameError(varname)
    
    def constrainGreater(self, greater, lesser):
        bigger = self.check(greater)
        smaller = self.check(lesser)
        #print "%s > %s: %s > %s" % (greater, lesser, bigger, smaller)
        self.problem += bigger > smaller
    
    def constrainEqual(self, left, right):
        first = self.check(left)
        second = self.check(right)
        #print "%s = %s: %s = %s" % (left, right, first, second)
        self.problem += first == second
    
    def setup(self, statement):
        self.problem = LpProblem(statement, LpMinimize)
        self.problem += sum(self.variables.values())
        
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
            #else:
            #    self.constrainEqual(ab, ba)
        
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
        #print self.problem
        status = self.problem.solve(COIN())
        return LpStatus[status]
    
    def report(self):
        values = [
            ((-LpValue(self.variables[name]), name) for name in self.variables),
            [(-self.total(), "Total")],
            ((-self.pairs[name](), name) for name in self.pairs),
            ((-self.candidates[name](), name) for name in self.candidates),
            ((-self.bordas[name](), "Borda-"+name) for name in self.bordas),
        ]
        
        for valueset in values:
            for value, name in sorted(valueset):
                print "%s = %s" % (name, -value)
        
        ballots = [(key.upper(), LpValue(self.variables[key])) for key in self.variables]
        for method in methods:
            result = methods[method](ballots, set(self.candidates))
            rewritten = " > ".join("=".join(sorted(r)) for r in result)
            print "%-8s\t%s" % (method+":", rewritten)
    
    def results(self):
        for name in sorted(self.variables):
            yield LpValue(self.variables[name])
        
        yield self.total()
        
        for name in sorted(self.pairs):
            yield self.pairs[name]()
        
        for name in sorted(self.candidates):
            yield self.candidates[name]()
        
        for name in sorted(self.bordas):
            yield self.bordas[name]()
        
        ballots = [(key.upper(), LpValue(self.variables[key])) for key in self.variables]
        for method in sorted(methods):
            result = methods[method](ballots, set(self.candidates))
            yield " > ".join("=".join(sorted(r)) for r in result)
    
    def headers(self):
        for name in sorted(self.variables):
            yield name
        
        yield "Total"
        
        for name in sorted(self.pairs):
            yield name
        
        for name in sorted(self.candidates):
            yield name
        
        for name in sorted(self.bordas):
            yield name
        
        for name in sorted(methods):
            yield name

def main(statement, winner=None):
    candidates = set(statement) - set("=>")
    if winner:
        assert winner in candidates
    solver = BallotFinder(candidates)
    solver.setup(statement)
    if winner:
        #solver.plurality(winner)
        solver.borda(winner)
    status = solver.solve()
    print "Status:", status
    solver.report()

if __name__ == "__main__":
    from sys import argv
    try:
        main(*argv[1:])
    except:
        print argv[0] + " 'AB>CD>BD=AD>BC>AC' [D]"
        raise
