from itertools import count

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

class CustomSolver(object):
    # Even Minion is getting too slow.
    # Maybe that's because it's such a general solver.
    
    def __init__(self):
        self.variables = OrderedDict()
        self.constraints = []
        self.sums = OrderedDict()
    
    def addVariables(self, varnames, minimum, maximum):
        for name in varnames:
            self.variables[name] = (maximum - minimum) // 2
    
    def check(self, varname):
        if varname in self.variables:
            return [varname]
        if varname in self.sums:
            return self.sums[varname]
        raise NameError(varname)
    
    def constrainGreater(self, greater, lesser):
        greater = self.check(greater)
        lesser = self.check(lesser)
        self.constraints.append((greater, lesser, True))
    
    def constrainEqual(self, first, second):
        first = self.check(first)
        second = self.check(second)
        self.constraints.append((first, second, False))
    
    def defineSum(self, varname, parts):
        self.sums[varname] = parts
    
    def solve(self):
        backsies = []
        for iteration in count(1):
            # Errors: negative contributions, positive contributions.
            # When sorted by value, variables too large should be at the head,
            # variables too small at the tail.
            errors = dict((key, [0, 0]) for key in self.variables)
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
                
                #print "%s %s %s" % (left, ">" if greater else "=", right)
                #print "Left: %s = %d" % (str.join(" + ", [str(self.variables[name]) for name in left]), left_hand)
                #print "Right: %s = %d" % (str.join(" + ", [str(self.variables[name]) for name in right]), right_hand)
                #print "Difference: %d" % difference
                
                for name in left:
                    errors[name][0] += left_bars[0]
                    errors[name][1] += left_bars[1]
                for name in right:
                    errors[name][0] += right_bars[0]
                    errors[name][1] += right_bars[1]
            
            if not total_errors:
                break
            
            varnames = list(self.variables)
            varnames.sort(key=errors.get)
            high = varnames[0]
            low = varnames[-1]
            
            if high in backsies or not self.variables[high]:
                high = varnames[1]
            if low in backsies:
                low = varnames[-2]
            backsies = [high, low]
            
            #for name in varnames:
            #    print ((name, self.variables[name], errors[name]))
            print ("%d: %d; moving 1 from %s (%d: %d/%d) to %s (%d: %d/%d)" % (
                    iteration, total_errors,
                    high, self.variables[high], errors[high][0], errors[high][1],
                    low, self.variables[low], errors[low][0], errors[low][1],
            ))
            
            self.variables[low] += 1
            if self.variables[high] >= 1:
                self.variables[high] -= 1
        
        for name in self.variables:
            print "%s = %s" % (name, self.variables[name])
        
        for name in self.sums:
            value = sum(self.variables[var] for var in self.sums[name])
            print "%s = %s" % (name, value)

class MinionSolver(object):
    # Install the minion program to use this solver.
    # http://minion.sourceforge.net/
    
    def __init__(self, filename):
        self.filename = filename
        self.variables = OrderedDict()
        self.constraints = []
        self.sums = OrderedDict()
    
    def addVariables(self, varnames, minimum, maximum):
        for name in varnames:
            self.variables[name] = "BOUND %s {%d..%d}" % (name, minimum, maximum)
    
    def check(self, varname):
        if varname in self.variables:
            return [varname]
        if varname in self.sums:
            return self.sums[varname]
        raise NameError(varname)
    
    def constrainGreater(self, greater, lesser):
        self.constraints.append("# %s > %s" % (greater, lesser))
        greater = self.check(greater)
        lesser = self.check(lesser)
        constants = [1] * len(greater) + [-1] * len(lesser)
        vector = str.join(",", greater + lesser)
        self.constraints.append("weightedsumgeq(%s,[%s],1)" % (constants, vector))
    
    def constrainEqual(self, first, second):
        self.constraints.append("# %s = %s" % (first, second))
        first = self.check(first)
        second = self.check(second)
        constants = [1] * len(first) + [-1] * len(second)
        vector = str.join(",", first + second)
        self.constraints.append("weightedsumgeq(%s,[%s],0)" % (constants, vector))
        self.constraints.append("weightedsumleq(%s,[%s],0)" % (constants, vector))
    
    def defineSum(self, varname, parts):
        self.sums[varname] = parts
    
    def solve(self):
        from subprocess import Popen, PIPE
        
        with open(self.filename, "w") as tmpfile:
            tmpfile.write("MINION 3\n\n")
            
            tmpfile.write("**VARIABLES**\n\n")
            for name in self.variables:
                line = self.variables[name]
                tmpfile.write(line + "\n")
            
            tmpfile.write("\n**CONSTRAINTS**\n\n")
            for line in self.constraints:
                tmpfile.write(line + "\n")
            
            tmpfile.write("\n**EOF**\n")
        
        output = Popen(["./minion", self.filename], stdout=PIPE).communicate()[0]
        values = [line[4:].strip() for line in output.split("\n") if line.startswith("Sol:")]
        
        results = {}
        if len(values) == len(self.variables):
            for name, value in zip(self.variables, values):
                print "%s = %s" % (name, value)
                results[name] = int(value)
        else:
            print output
        
        for name in self.sums:
            value = sum(results[var] for var in self.sums[name])
            print "%s = %s" % (name, value)

def solve(candidates, statement, solver, winner=None):
    from itertools import combinations, permutations
    
    statement = statement.split(">")
    perms = [str.join("", perm) for perm in permutations(candidates.lower())]
    solver.addVariables(perms, 0, 20)
    
    for a, b in combinations(candidates, 2):
        ab = a + b
        ba = b + a
        solver.defineSum(ab, [perm for perm in perms if perm.find(a.lower()) < perm.find(b.lower())])
        solver.defineSum(ba, [perm for perm in perms if perm.find(b.lower()) < perm.find(a.lower())])
        
        if ab in statement:
            solver.constrainGreater(ab, ba)
        elif ba in statement:
            solver.constrainGreater(ba, ab)
        else:
            solver.constrainEqual(ab, ba)
    
    for n in range(1, len(statement)):
        solver.constrainGreater(statement[n-1], statement[n])
    
    for c in candidates:
        solver.defineSum(c, [perm for perm in perms if perm.startswith(c.lower())])
    
    if winner:
        # Rig the election to have a specific winner
        for c in candidates:
            if c != winner:
                solver.constrainGreater(winner, c)
    
    solver.solve()

if __name__ == "__main__":
    solve("ABCD", "AB>CD>BD>AD>BC>AC", CustomSolver(), "D")
    #solve("ABC", "AB>AC>BC", CustomSolver(), "B")
