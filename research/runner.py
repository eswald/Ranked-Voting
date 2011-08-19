from matrixexpansion import BallotFinder
from permutations import with_equality

def main(candidates = "ABCD"):
    solver = BallotFinder(candidates)
    print ",".join(["Statement", "Borda", "Plurality", "Result"] + list(solver.headers()))
    for statement in with_equality(candidates):
        for bc in candidates:
            for pc in candidates:
                solver.setup(statement)
                solver.plurality(pc)
                solver.borda(bc)
                status = solver.solve()
                results = list(map(str, solver.results())) if status != "Infeasible" else []
                print ",".join([statement, bc, pc, status] + results)

if __name__ == "__main__":
    from sys import argv
    main(*argv[1:])
