from tests import VotingTestCase
from voting import *

class TenesseeTestCase(VotingTestCase):
    candidates = ["Memphis", "Nashville", "Chattanooga", "Knoxville"]
    M, N, C, K = 0, 1, 2, 3
    case = [
        ([M, N, C, K], 42),
        ([N, C, K, M], 26),
        ([C, K, N, M], 15),
        ([K, C, N, M], 17),
    ]
    
    def test_pairs(self):
        result = list(rankedpairs(self.case))
        self.assertEqual(result, [N, C, K, M])
    
    def test_irv(self):
        result = list(instantrunoff(self.case))
        self.assertEqual(result, [K, M, N, C])
    
    def test_plural(self):
        result = list(plurality(self.case))
        self.assertEqual(result, [M, N, K, C])

class UniversalTestCase(VotingTestCase):
    candidates = ["Best", "Maybe", "Possibly", "Reviled"]
    case = [
        ([0, 1, 2, 3], 3),
        ([0, 2, 1, 3], 2),
    ]
    
    def test_pairs(self):
        result = list(rankedpairs(self.case))
        self.assertEqual(result, [0, 1, 2, 3])
    
    def test_irv(self):
        result = list(instantrunoff(self.case))
        self.assertEqual(result, [0, 1, 2, 3])
    
    def test_plural(self):
        result = list(plurality(self.case))
        self.assertEqual(result, [0, (1, 2, 3)])

class MajorityTestCase(VotingTestCase):
    # Majority criterion -- If there exists a majority that ranks a single
    # candidate higher than all other candidates, does that candidate win?
    candidates = ["Best", "Maybe", "Possibly", "Reviled"]
    case = [
        ([0, 1, 2, 3], 6),
        ([0, 2, 1, 3], 5),
        ([1, 2, 0, 3], 4),
        ([2, 1, 0, 3], 3),
        ([1, 0, 2, 3], 2),
        ([2, 0, 1, 3], 1),
    ]
    
    def test_pairs(self):
        result = list(rankedpairs(self.case))
        self.assertEqual(result, [0, 1, 2, 3])
    
    def test_irv(self):
        result = list(instantrunoff(self.case))
        self.assertEqual(result, [0, 1, 2, 3])
    
    def test_plural(self):
        result = list(plurality(self.case))
        self.assertEqual(result, [0, 1, 2, 3])

