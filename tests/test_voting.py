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
        self.assertEqual(self.results[method], result)
    
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

class PluralityTestCase(MethodTestCase):
    r'''Demonstration of severe vote-splitting.
        http://fc.antioch.edu/~james_green-armytage/vm/survey.htm#plurality
        
        Plurality is the only method that would elect a far-right candidate
        when over 80% of the voters prefer a leftist candidate.
        IRV places the right-winger higher in the rankings that it should be,
        but even it doesn't float the loser all the way to the top.
    '''#"""#'''
    
    candidates = range(9)
    
    ballots = [
        ([0, (1, 2, 3, 4, 5, 6, 7, 8)], 20),
        ([1, (2, 3, 4, 5, 6, 7, 8), 0], 13),
        ([2, (1, 3, 4, 5, 6, 7, 8), 0], 11),
        ([3, (1, 2, 4, 5, 6, 7, 8), 0], 10),
        ([4, (1, 2, 3, 5, 6, 7, 8), 0], 10),
        ([5, (1, 2, 3, 4, 6, 7, 8), 0], 10),
        ([6, (1, 2, 3, 4, 5, 7, 8), 0], 10),
        ([7, (1, 2, 3, 4, 5, 6, 8), 0], 9),
        ([8, (1, 2, 3, 4, 5, 6, 7), 0], 7),
    ]
    
    results = {
        rankedpairs: [1, 2, (3, 4, 5, 6), 7, 8, 0],
        instantrunoff: [1, 2, 0, (3, 4, 5, 6), 7, 8],
        plurality: [0, 1, 2, (3, 4, 5, 6), 7, 8],
        borda: [1, 2, (3, 4, 5, 6), 7, 8, 0],
    }

class RunoffTestCase(MethodTestCase):
    r'''Demonstration of Instant runoff voting.
        http://fc.antioch.edu/~james_green-armytage/vm/survey.htm#irv
        
        The Far Left candidate splits the leftist vote under plurality,
        but contributes to the Left win under other systems.
        Whether Right or Far Left should be second is up for debate.
    '''#"""#'''
    
    candidates = ["Far Left", "Left", "Right", "Far Right"]
    
    ballots = [
        (["Far Right", "Right", "Left", "Far Left"], 5),
        (["Right", "Far Right", "Left", "Far Left"], 40),
        (["Left", "Far Left", "Right", "Far Right"], 36),
        (["Far Left", "Left", "Right", "Far Right"], 19),
    ]
    
    results = {
        rankedpairs: ["Left", "Far Left", "Right", "Far Right"],
        instantrunoff: ["Left", "Right", "Far Left", "Far Right"],
        plurality: ["Right", "Left", "Far Left", "Far Right"],
        borda: ["Left", "Right", "Far Left", "Far Right"],
    }

class CondorcetTestCase(MethodTestCase):
    r'''Demonstration of the Condorcet principle.
        http://fc.antioch.edu/~james_green-armytage/vm/survey.htm#condorcet
        
        The Center candidate doesn't seem like a strong contender,
        but is a decent compromise between the two polarized sides.
        It would beat either one in a head-to-head battle.
        Unfortunately, neither Plurality nor IRV see that.
    '''#"""#'''
    
    candidates = ["Left", "Center", "Right"]
    
    ballots = [
        (["Left", "Center", "Right"], 33),
        (["Center", "Left", "Right"], 16),
        (["Center", "Right", "Left"], 16),
        (["Right", "Center", "Left"], 35),
    ]
    
    results = {
        rankedpairs: ["Center", "Right", "Left"],
        instantrunoff: ["Right", "Left", "Center"],
        plurality: ["Right", "Left", "Center"],
        borda: ["Center", "Right", "Left"],
    }

class MinimaxTestCase(MethodTestCase):
    r'''Demonstration of the Minimax resolution of non-Condorcet elections.
        http://fc.antioch.edu/~james_green-armytage/vm/survey.htm#minimax
        
        Imaginary election slightly based on the 2000 U.S. presidential candidates.
        The truncated ballots in the example have been expanded.
    '''#"""#'''
    
    candidates = ["Bush", "Gore", "Nader"]
    
    ballots = [
        (["Bush", ("Gore", "Nader")], 45),
        (["Gore", ("Bush", "Nader")], 12),
        (["Gore", "Nader", "Bush"], 14),
        (["Nader", "Gore", "Bush"], 29),
    ]
    
    results = {
        rankedpairs: ["Gore", "Bush", "Nader"],
        instantrunoff: ["Bush", "Nader", "Gore"],
        plurality: ["Bush", "Nader", "Gore"],
        borda: ["Gore", "Nader", "Bush"],
        minimax: ["Gore", "Bush", "Nader"],
    }

class SmithSetTestCase(MethodTestCase):
    r'''Demonstration of the Minimax failure mode.
        http://fc.antioch.edu/~james_green-armytage/vm/survey.htm#smith
        
        Candidate D is a Condorcet loser, so should not be able to win.
    '''#"""#'''
    
    candidates = "ABCD"
    
    ballots = [
        ("ABCD", 6),
        ("DCAB", 6),
        ("BCAD", 6),
        ("DABC", 5),
        ("CABD", 4),
        ("DBCA", 4),
        ("BCDA", 2),
        ("ACBD", 2),
        ("ACDB", 1),
    ]
    
    results = {
        rankedpairs: ["A", "B", "C", "D"],
        instantrunoff: ["A", "D", "B", "C"],
        plurality: ["D", "A", "B", "C"],
        borda: ["A", "C", "B", "D"],
        minimax: ["D", "A", "B", "C"],
    }

