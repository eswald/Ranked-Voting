
class MinionSolver(object):
    # Install the minion program to use this solver.
    # http://minion.sourceforge.net/
    
    def __init__(self, filename):
        self.filename = filename
        self.variables = []
        self.constraints = []
    
    def addVariables(self, varnames, minimum, maximum):
        for name in varnames:
            self.variables.append("DISCRETE %s {%d..%d}" % (name, minimum, maximum))
    
    def constrainGreater(self, greater, lesser):
        self.constraints.append("weightedsumgeq([1,-1],[%s,%s],1)" % (greater, lesser))
    
    def constrainEqual(self, *varnames):
        self.constraints.append("eq(%s,%s)" % varnames)
    
    def defineSum(self, varname, parts):
        vector = str.join(",", parts)
        constants = str.join(",", ["1"] * len(vector.split(",")))
        self.constraints.append("weightedsumgeq([%s,-1],[%s,%s],0)" % (constants, vector, varname))
        self.constraints.append("weightedsumleq([%s,-1],[%s,%s],0)" % (constants, vector, varname))
    
    def solve(self):
        from subprocess import Popen, PIPE
        
        with open(self.filename, "w") as tmpfile:
            tmpfile.write("MINION 3\n\n")
            
            tmpfile.write("**VARIABLES**\n\n")
            for line in self.variables:
                tmpfile.write(line + "\n")
            
            tmpfile.write("\n**CONSTRAINTS**\n\n")
            for line in self.constraints:
                tmpfile.write(line + "\n")
            
            tmpfile.write("\n**EOF**\n")
        
        output = Popen(["./minion", self.filename], stdout=PIPE).communicate()[0]
        values = [line[4:].strip() for line in output.split("\n") if line.startswith("Sol:")]
        if len(values) == len(self.variables):
            for line, value in zip(self.variables, values):
                varname = line.split(" ")[1]
                print "%s = %s" % (varname, value)
        else:
            print output

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

def solve(candidates, statement, solver, winner=None):
    from itertools import combinations, permutations
    
    statement = statement.split(">")
    perms = [str.join("", perm) for perm in permutations(candidates.lower())]
    solver.addVariables(candidates, 1, 99)
    solver.addVariables(perms, 0, 20)
    
    for a, b in combinations(candidates, 2):
        ab = a + b
        ba = b + a
        solver.addVariables([ab, ba], 1, 99)
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
    
    if winner:
        # Rig the election to have a specific winner
        for c in candidates:
            solver.defineSum(c, (perm for perm in perms if perm.startswith(c.lower())))
            if c != winner:
                solver.constrainGreater(winner, c)
    
    solver.solve()

if __name__ == "__main__":
    #solve("ABCD", "AB>AC>AD>BC>BD>CD", MinionSolver("ab-ac-ad-bc-bd-cd"))
    solve("ABC", "AB>AC>BC", MinionSolver("ab-ac-bc"), "B")
