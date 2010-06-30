from tests import VotingTestCase
from voting import *

class TenesseeTestCase(VotingTestCase):
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

class MajorityTestCase(VotingTestCase):
    # Majority criterion -- If there exists a majority that ranks a single
    # candidate higher than all other candidates, does that candidate win?
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

