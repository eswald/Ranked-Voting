
class PythonSolver(object):
    # Install the python-constraint package to use this solver.
    # Pure Python, but very slow.
    
    def __init__(self):
        from constraint import Problem
        self.problem = Problem()
        self.varnames = []
    
    def addVariables(self, varnames, minimum, maximum):
        varnames = list(varnames)
        self.varnames.extend(varnames)
        self.problem.addVariables(varnames, range(minimum, maximum + 1))
    
    def constrainGreater(self, greater, lesser):
        from operator import gt
        self.problem.addConstraint(gt, [greater, lesser])
    
    def constrainEqual(self, *varnames):
        from constraint import AllEqualConstraint
        self.problem.addConstraint(AllEqualConstraint(), *varnames)
    
    def defineSum(self, varname, parts):
        def total(name, *parts):
            return name == sum(parts)
        
        self.problem.addConstraint(total, [varname] + list(parts))
    
    def solve(self):
        solution = self.problem.getSolution()
        for varname in self.varnames:
            print "%s = %d" % (varname, solution[varname])

def solve(candidates, statement, solver):
    from itertools import combinations, permutations
    
    statement = statement.split(">")
    perms = [str.join("", perm) for perm in permutations(candidates.lower())]
    solver.addVariables(candidates, 1, 999)
    solver.addVariables(perms, 1, 99)
    
    for a, b in combinations(candidates, 2):
        ab = a + b
        ba = b + a
        solver.addVariables([ab, ba], 1, 999)
        solver.defineSum(ab, (perm for perm in perms if perm.find(a.lower()) < perm.find(b.lower())))
        solver.defineSum(ba, (perm for perm in perms if perm.find(b.lower()) < perm.find(a.lower())))
        
        if ab in statement:
            solver.constrainGreater(ab, ba)
        elif ba in statement:
            solver.constrainGreater(ba, ab)
        else:
            solver.constrainEqual(ab, ba)
    
    for n in range(1, len(statement)):
        solver.constrainGreater(statement[n-1], statement[n])
    
    # Plurality rankings
    for c in candidates:
        solver.defineSum(c, (perm for perm in perms if perm.startswith(c.lower())))
    
    # Question: Can the second-ranked candidate win a plurality election?
    #solver.constrainGreater("B", "A")
    
    solver.solve()

if __name__ == "__main__":
    solve("ABCD", "AB>AC>AD>BC>BD>CD", PythonSolver())
