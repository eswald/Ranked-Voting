from tests import VotingTestCase
from voting import *

class MethodTestCase(VotingTestCase):
    r'''Base class for testing the voting methods.
        Each TestCase class presents a single election.
        Subclasses need only override results, ballots, and probably candidates.
        
        This case is a very simple election that should be unambiguous.
    '''#"""#'''
    
    candidates = {
        0: "Best",
        1: "Maybe",
        2: "Possibly",
        3: "Reviled",
    }
    
    ballots = [
        ([0, 1, 2, 3], 4),
        ([0, 2, 1, 3], 3),
        ([1, 0, 2, 3], 2),
        ([2, 0, 1, 3], 1),
    ]
    
    results = {
        rankedpairs: [0, 1, 2, 3],
        instantrunoff: [0, 1, 2, 3],
        plurality: [0, 1, 2, 3],
        borda: [0, 1, 2, 3],
    }
    
    def check_method(self, method):
        result = list(method(self.ballots, self.candidates))
        self.assertEqual(result, self.results[method])
    
    def test_rankedpairs(self):
        self.check_method(rankedpairs)
    
    def test_instantrunoff(self):
        self.check_method(instantrunoff)
    
    def test_plurality(self):
        self.check_method(plurality)
    
    def test_borda(self):
        self.check_method(borda)

class TenesseeTestCase(MethodTestCase):
    r'''Hypothetical election to select a state capital.
        Described on the Wikipedia pages for certain voting methods:
            - http://en.wikipedia.org/wiki/Condorcet_method
            - http://en.wikipedia.org/wiki/Ranked_Pairs
            - http://en.wikipedia.org/wiki/Borda_count
        
        Each city votes to get the capital as close as possible,
        with the strength of its respective population.
        Nashville, as the centermost city, is the Condorcet winner,
        but Knoxville and Memphis can be elected by other methods.
    '''#"""#'''
    
    candidates = [
        "Memphis",
        "Nashville",
        "Chattanooga",
        "Knoxville",
    ]
    
    ballots = [
        (["Memphis", "Nashville", "Chattanooga", "Knoxville"], 42),
        (["Nashville", "Chattanooga", "Knoxville", "Memphis"], 26),
        (["Chattanooga", "Knoxville", "Nashville", "Memphis"], 15),
        (["Knoxville", "Chattanooga", "Nashville", "Memphis"], 17),
    ]
    
    results = {
        rankedpairs: ["Nashville", "Chattanooga", "Knoxville", "Memphis"],
        instantrunoff: ["Knoxville", "Memphis", "Nashville", "Chattanooga"],
        plurality: ["Memphis", "Nashville", "Knoxville", "Chattanooga"],
        borda: ["Nashville", "Chattanooga", "Memphis", "Knoxville"],
    }

class MajorityTestCase(MethodTestCase):
    r'''Test case for the Majority Criterion.
        http://en.wikipedia.org/wiki/Borda_count
        
        If a majority ranks a single candidate higher than all others,
        that candidate should probably win.
        However, Borda count can produce a different result.
        In this case, the majority winner is hated by a large minority,
        while Catherine is at least second place for everyone.
    '''#"""#'''
    
    candidates = ["Andrew", "Brian", "Catherine", "David"]
    
    ballots = [
        (["Andrew", "Catherine", "Brian", "David"], 51),
        (["Catherine", "Brian", "David", "Andrew"], 5),
        (["Brian", "Catherine", "David", "Andrew"], 23),
        (["David", "Catherine", "Brian", "Andrew"], 21),
    ]
    
    results = {
        rankedpairs: ["Andrew", "Catherine", "Brian", "David"],
        instantrunoff: ["Andrew", "Catherine", "Brian", "David"],
        plurality: ["Andrew", "Brian", "David", "Catherine"],
        borda: ["Catherine", "Andrew", "Brian", "David"],
    }

class EqualRanksTestCase(MethodTestCase):
    r'''Voting methods should allow equal rankings at any level.
        The canonical versions of most voting methods don't, unfortunately.
    '''#"""#'''
    
    ballots = [
        ([0, (1, 2), 3], 6),
        ([1, 2, (0, 3)], 4),
        ([2, 3, 1, 0], 3),
        ([(1, 0), 2, 3], 2),
        ([0, 2, (1, 3)], 1),
    ]
    
    results = {
        rankedpairs: [(0, 1), 2, 3],
        instantrunoff: [(0, 1), 2, 3],
        plurality: [0, 1, 2, 3],
        borda: [2, 1, 0, 3],
    }

class MonotonicityTestCase(MethodTestCase):
    r'''First part of the test case for the Monotonicity Criterion:
        http://en.wikipedia.org/wiki/Monotonicity_criterion
        
        This is the original ballot, with three strong candidates.
    '''#"""#'''
    
    candidates = ["Andrea", "Belinda", "Cynthia"]
    
    ballots = [
        (["Andrea", "Belinda", "Cynthia"], 39),
        (["Belinda", "Cynthia", "Andrea"], 35),
        (["Cynthia", "Andrea", "Belinda"], 26),
    ]
    
    results = {
        rankedpairs: ["Andrea", "Belinda", "Cynthia"],
        instantrunoff: ["Andrea", "Belinda", "Cynthia"],
        plurality: ["Andrea", "Belinda", "Cynthia"],
        borda: ["Belinda", "Andrea", "Cynthia"],
    }

class Monotonicity2TestCase(MonotonicityTestCase):
    r'''Second part of the test case for the Monotonicity Criterion:
        http://en.wikipedia.org/wiki/Monotonicity_criterion
        
        Andrea has served well, impressing ten of Belinda's supporters to
        change their votes.  That shouldn't hurt Andrea, nor should it help
        Belinda or Cynthia, but it does under IRV.
    '''#"""#'''
    
    ballots = [
        (["Andrea", "Belinda", "Cynthia"], 49),
        (["Belinda", "Cynthia", "Andrea"], 25),
        (["Cynthia", "Andrea", "Belinda"], 26),
    ]
    
    results = {
        rankedpairs: ["Andrea", "Belinda", "Cynthia"],
        instantrunoff: ["Cynthia", "Andrea", "Belinda"],
        plurality: ["Andrea", "Cynthia", "Belinda"],
        borda: ["Andrea", "Belinda", "Cynthia"],
    }

