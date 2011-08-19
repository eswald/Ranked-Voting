from matrixexpansion import BallotFinder
from permutations import with_equality

def main(candidates = "ABCD"):
    solver = BallotFinder(candidates)
    print ",".join(["Statement", "Plurality", "Borda", "Result"] + list(solver.headers()))
    for statement in with_equality(candidates):
        for pc in candidates:
            for bc in candidates:
                solver.setup(statement)
                solver.plurality(pc)
                solver.borda(bc)
                status = solver.solve()
                print ",".join([statement, pc, bc, status] + list(map(str, solver.results())))

if __name__ == "__main__":
    from sys import argv
    main(*argv[1:])
