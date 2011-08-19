from matrixexpansion import BallotFinder
from permutations import with_equality

def main(candidates = "ABCD"):
    solver = BallotFinder(candidates)
    print ",".join(["Statement", "Borda", "Plurality", "Result"] + list(solver.headers()))
    for statement in with_equality(candidates):
        valid = check(solver, statement, None, None)
        if not valid:
            continue
        
        retries = set(candidates)
        for bc in candidates:
            valid = check(solver, statement, bc, None)
            if not valid:
                continue
            
            for pc in candidates:
                valid = check(solver, statement, bc, pc)
                if valid:
                    retries.discard(pc)
        
        for pc in retries:
            check(solver, statement, None, pc)

def check(solver, statement, bc, pc):
    solver.setup(statement)
    if bc:
        solver.borda(bc)
    if pc:
        solver.plurality(pc)
    status = solver.solve()
    results = list(map(str, solver.results())) if status != "Infeasible" else []
    print ",".join([statement, bc or "", pc or "", status] + results)
    return status != "Infeasible"

if __name__ == "__main__":
    from sys import argv
    main(*argv[1:])
