from tests import VotingTestCase
from voting import *

class TenesseeTestCase(VotingTestCase):
    # Hypothetical election to select a state capital.
    # http://en.wikipedia.org/wiki/Borda_count
    
    candidates = {
        0: "Memphis",
        1: "Nashville",
        2: "Chattanooga",
        3: "Knoxville",
    }
    
    case = [
        ([0, 1, 2, 3], 42),
        ([1, 2, 3, 0], 26),
        ([2, 3, 1, 0], 15),
        ([3, 2, 1, 0], 17),
    ]
    
    def test_pairs(self):
        result = list(rankedpairs(self.case, self.candidates))
        self.assertEqual(result, [1, 2, 3, 0])
    
    def test_irv(self):
        result = list(instantrunoff(self.case, self.candidates))
        self.assertEqual(result, [3, 0, 1, 2])
    
    def test_plural(self):
        result = list(plurality(self.case, self.candidates))
        self.assertEqual(result, [0, 1, 3, 2])
    
    def test_borda(self):
        result = list(borda(self.case, self.candidates))
        self.assertEqual(result, [1, 2, 0, 3])

class UniversalTestCase(VotingTestCase):
    candidates = {
        0: "Best",
        1: "Maybe",
        2: "Possibly",
        3: "Reviled",
    }
    
    case = [
        ([0, 1, 2, 3], 3),
        ([0, 2, 1, 3], 2),
    ]
    
    def test_pairs(self):
        result = list(rankedpairs(self.case, self.candidates))
        self.assertEqual(result, [0, 1, 2, 3])
    
    def test_irv(self):
        result = list(instantrunoff(self.case, self.candidates))
        self.assertEqual(result, [0, 1, 2, 3])
    
    def test_plural(self):
        result = list(plurality(self.case, self.candidates))
        self.assertEqual(result, [0, (1, 2, 3)])
    
    def test_borda(self):
        result = list(borda(self.case, self.candidates))
        self.assertEqual(result, [0, 1, 2, 3])

class ReviledTestCase(VotingTestCase):
    # A candidate ranked last by everyone should not win.
    # This case is just a bit more complex than the Universal one.
    candidates = {
        0: "Best",
        1: "Maybe",
        2: "Possibly",
        3: "Reviled",
    }
    
    case = [
        ([0, 1, 2, 3], 6),
        ([0, 2, 1, 3], 5),
        ([1, 2, 0, 3], 4),
        ([2, 1, 0, 3], 3),
        ([1, 0, 2, 3], 2),
        ([2, 0, 1, 3], 1),
    ]
    
    def test_pairs(self):
        result = list(rankedpairs(self.case, self.candidates))
        self.assertEqual(result, [0, 1, 2, 3])
    
    def test_irv(self):
        result = list(instantrunoff(self.case, self.candidates))
        self.assertEqual(result, [0, 1, 2, 3])
    
    def test_plural(self):
        result = list(plurality(self.case, self.candidates))
        self.assertEqual(result, [0, 1, 2, 3])
    
    def test_borda(self):
        result = list(borda(self.case, self.candidates))
        self.assertEqual(result, [0, 1, 2, 3])

class MajorityTestCase(VotingTestCase):
    # Majority criterion -- If there exists a majority that ranks a single
    # candidate higher than all other candidates, does that candidate win?
    # http://en.wikipedia.org/wiki/Borda_count
    
    candidates = ["Andrew", "Brian", "Catherine", "David"]
    
    case = [
        (["Andrew", "Catherine", "Brian", "David"], 51),
        (["Catherine", "Brian", "David", "Andrew"], 5),
        (["Brian", "Catherine", "David", "Andrew"], 23),
        (["David", "Catherine", "Brian", "Andrew"], 21),
    ]
    
    def test_pairs(self):
        result = list(rankedpairs(self.case, self.candidates))
        self.assertEqual(result, ["Andrew", "Catherine", "Brian", "David"])
    
    def test_irv(self):
        result = list(instantrunoff(self.case, self.candidates))
        self.assertEqual(result, ["Andrew", "Catherine", "Brian", "David"])
    
    def test_plural(self):
        result = list(plurality(self.case, self.candidates))
        self.assertEqual(result, ["Andrew", "Brian", "David", "Catherine"])
    
    def test_borda(self):
        # Andrew has a clear majority, but is hated by almost half.
        # Catherine is at least second place for everybody.
        result = list(borda(self.case, self.candidates))
        self.assertEqual(result, ["Catherine", "Andrew", "Brian", "David"])

class EqualRanksTestCase(VotingTestCase):
    # Voting methods should accept tuples to indicate equal ranks.
    candidates = range(4)
    votes = [
        ([0, (1, 2), 3], 6),
        ([1, 2, (0, 3)], 4),
        ([2, 3, 1, 0], 3),
        ([(1, 0), 2, 3], 2),
        ([0, 2, (1, 3)], 1),
    ]
    
    def test_pairs(self):
        # 0/1:  +7 -7  =
        # 0/2:  +9 -7  +
        # 0/3:  +9 -3  +
        # 1/2:  +6 -4  +
        # 1/3: +12 -3  +
        # 2/3: +16 -0  +
        result = list(rankedpairs(self.votes, self.candidates))
        self.assertEqual(result, [(0, 1), 2, 3])
    
    def test_irv(self):
        # 0: 8, 1: 5, 2: 3, 3: 0
        # 0: 8, 1: 8
        result = list(instantrunoff(self.votes, self.candidates))
        self.assertEqual(result, [(0, 1), 2, 3])
    
    def test_plural(self):
        # 0: 8, 1: 5, 2: 3, 3: 0
        result = list(plurality(self.votes, self.candidates))
        self.assertEqual(result, [0, 1, 2, 3])
    
    def test_borda(self):
        # 18   9     9  0
        #  2  12     8  2
        #  0   3     9  6
        #  5   5     2  0
        #  3   0.5   2  0.5
        # 28  29.5  30  8.5
        result = list(borda(self.votes, self.candidates))
        self.assertEqual(result, [2, 1, 0, 3])

class MonotonicityTestCase(VotingTestCase):
    # Increasing a candidate's rating should not hurt,
    # and decreasing a rating should not help.
    # http://en.wikipedia.org/wiki/Monotonicity_criterion
    
    candidates = set("ABC")
    original = [
        (["A", "B", "C"], 39),
        (["B", "C", "A"], 35),
        (["C", "A", "B"], 26),
    ]
    
    later = [
        (["A", "B", "C"], 49),
        (["B", "C", "A"], 25),
        (["C", "A", "B"], 26),
    ]
    
    def test_irv(self):
        # Instant Runoff Voting fails this criterion.
        # This test just asserts that our implementation follows spec.
        result = list(instantrunoff(self.original, self.candidates))
        self.assertEqual(result, ["A", "B", "C"])
        
        result = list(instantrunoff(self.later, self.candidates))
        self.assertEqual(result, ["C", "A", "B"])
    
    def test_plural(self):
        # Plurality passes this criterion for the first place winner,
        # but not for ordering the remaining candidates.
        result = list(plurality(self.original, self.candidates))
        self.assertEqual(result, ["A", "B", "C"])
        
        result = list(plurality(self.later, self.candidates))
        self.assertEqual(result, ["A", "C", "B"])
    
    def test_pairs(self):
        # Ranked pairs passes this criterion.
        result = list(rankedpairs(self.original, self.candidates))
        self.assertEqual(result, ["A", "B", "C"])
        
        result = list(rankedpairs(self.later, self.candidates))
        self.assertEqual(result, ["A", "B", "C"])
    
    def test_borda(self):
        # A misses the first election by a hair,
        # but gets redeemed by the ten extra votes.
        
        # 104  109  87
        result = list(borda(self.original, self.candidates))
        self.assertEqual(result, ["B", "A", "C"])
        
        # 124  99  77
        result = list(borda(self.later, self.candidates))
        self.assertEqual(result, ["A", "B", "C"])

