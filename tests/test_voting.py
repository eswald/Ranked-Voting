from tests import VotingTestCase
from voting import unwind
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
        beatpath: [0, 1, 2, 3],
        river: [0, 1, 2, 3],
        instantrunoff: [0, 1, 2, 3],
        plurality: [0, 1, 2, 3],
        bucklin: [0, 1, 2, 3],
        borda: [0, 1, 2, 3],
        minimax: [0, 1, 2, 3],
    }
    
    def check_method(self, method):
        result = list(method(self.ballots, self.candidates))
        self.assertEqual(self.results[method], result)
    
    def test_rankedpairs(self):
        self.check_method(rankedpairs)
    
    def test_beatpath(self):
        self.check_method(beatpath)
    
    def test_river(self):
        self.check_method(river)
    
    def test_instantrunoff(self):
        self.check_method(instantrunoff)
    
    def test_plurality(self):
        self.check_method(plurality)
    
    def test_bucklin(self):
        self.check_method(bucklin)
    
    def test_borda(self):
        self.check_method(borda)
    
    def test_minimax(self):
        self.check_method(minimax)

class CriterionTestCase(MethodTestCase):
    r'''Base class for testing voting method criteria.
        Each TestCase class presents a series of elections.
        Subclasses need only override results, ballots, probably candidates,
        and the check_results() function.
        
        This case simply tests that the results are always consistent.
    '''#"""#'''
    
    candidates = {
        0: "Best",
        1: "Maybe",
        2: "Possibly",
        3: "Reviled",
    }
    
    ballots = [
        [
            ([0, 1, 2, 3], 4),
            ([0, 2, 1, 3], 3),
            ([1, 0, 2, 3], 2),
            ([2, 0, 1, 3], 1),
        ],
        [
            ([0, 1, 2, 3], 4),
            ([0, 2, 1, 3], 3),
            ([1, 0, 2, 3], 2),
            ([2, 0, 1, 3], 1),
        ],
    ]
    
    results = {
        rankedpairs: True,
        beatpath: True,
        river: True,
        instantrunoff: True,
        plurality: True,
        bucklin: True,
        borda: True,
        minimax: True,
    }
    
    def check_results(self, results):
        r'''Given a set of results, one per election, check the criterion.'''
        return results[0] == results[1]
    
    def check_method(self, method):
        result = self.check_results([list(method(election, self.candidates))
                for election in self.ballots])
        self.assertEqual(self.results[method], result)

class TenesseeTestCase(MethodTestCase):
    r'''Hypothetical election to select a state capital.
        Described on the Wikipedia pages for certain voting methods:
            - http://en.wikipedia.org/wiki/Condorcet_method
            - http://en.wikipedia.org/wiki/Ranked_Pairs
            - http://en.wikipedia.org/wiki/Borda_count
            - http://en.wikipedia.org/wiki/Bucklin_voting
        
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
        beatpath: ["Nashville", "Chattanooga", "Knoxville", "Memphis"],
        river: ["Nashville", "Chattanooga", "Knoxville", "Memphis"],
        instantrunoff: ["Knoxville", "Memphis", "Nashville", "Chattanooga"],
        plurality: ["Memphis", "Nashville", "Knoxville", "Chattanooga"],
        bucklin: ["Nashville", "Chattanooga", "Memphis", "Knoxville"],
        borda: ["Nashville", "Chattanooga", "Memphis", "Knoxville"],
        minimax: ["Nashville", "Chattanooga", "Knoxville", "Memphis"],
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
        beatpath: ["Andrew", "Catherine", "Brian", "David"],
        river: ["Andrew", "Catherine", "Brian", "David"],
        instantrunoff: ["Andrew", "Catherine", "Brian", "David"],
        plurality: ["Andrew", "Brian", "David", "Catherine"],
        bucklin: ["Andrew", "Brian", "David", "Catherine"],
        borda: ["Catherine", "Andrew", "Brian", "David"],
        minimax: ["Andrew", "Catherine", "Brian", "David"],
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
        beatpath: [(0, 1), 2, 3],
        river: [(0, 1), 2, 3],
        instantrunoff: [(0, 1), 2, 3],
        plurality: [0, 1, 2, 3],
        bucklin: [2, (0, 1), 3],
        borda: [2, 1, 0, 3],
        minimax: [(0, 1), 2, 3],
    }

class MonotonicityTestCase(CriterionTestCase):
    r'''Test case for the Monotonicity Criterion:
        http://en.wikipedia.org/wiki/Monotonicity_criterion
        
        A candidate should not be harmed by being raised on some ballots
        without changing the orders of the other candidates.
        
        In this case, Andrea gets elected, serving well enough to collect the
        top vote from ten of Belinda's original supporters.  That should help
        Andrea secure the second election, but she loses under IRV.
    '''#"""#'''
    
    candidates = ["Andrea", "Belinda", "Cynthia"]
    
    ballots = [
        [
            (["Andrea", "Belinda", "Cynthia"], 39),
            (["Belinda", "Cynthia", "Andrea"], 35),
            (["Cynthia", "Andrea", "Belinda"], 26),
        ],
        [
            (["Andrea", "Belinda", "Cynthia"], 49),
            (["Belinda", "Cynthia", "Andrea"], 25),
            (["Cynthia", "Andrea", "Belinda"], 26),
        ],
    ]
    
    results = {
        rankedpairs: True,
        beatpath: True,
        river: True,
        instantrunoff: False,
        plurality: True,
        bucklin: True,
        borda: True,
        minimax: True,
    }
    
    def check_results(self, results):
        def position(result, candidate):
            for n, rank in enumerate(unwind(result)):
                if candidate in rank:
                    return n
        
        return position(results[0], "Andrea") >= position(results[1], "Andrea")

class ReversalTestCase(CriterionTestCase):
    r'''Test case for the Reversal Symmetry Criterion:
        http://en.wikipedia.org/wiki/Reversal_symmetry
        
        If a candidate is the unique winner, then that candidate must not win
        an election in which each voter's preferences are inverted.
    '''#"""#'''
    
    candidates = "ABCD"
    
    ballots = [
        [
            ("ABCD", 5),
            ("BCDA", 4),
            ("CDAB", 2),
        ],
        [
            ("DCBA", 5),
            ("ADCB", 4),
            ("BADC", 2),
        ],
        [
            ("ABC", 22),
            ("ACB", 23),
            ("BAC", 6),
            ("BCA", 20),
            ("CBA", 29),
        ],
        [
            ("CBA", 22),
            ("BCA", 23),
            ("CAB", 6),
            ("ACB", 20),
            ("ABC", 29),
        ],
    ]
    
    results = {
        rankedpairs: True,
        beatpath: True,
        river: True,
        instantrunoff: False,
        plurality: False,
        bucklin: False,
        borda: True,
        minimax: False,
    }
    
    def check_results(self, results):
        return results[0][0] != results[1][0] and results[2][0] != results[3][0]

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
        beatpath: [1, 2, (3, 4, 5, 6), 7, 8, 0],
        river: [1, 2, (3, 4, 5, 6), 7, 8, 0],
        instantrunoff: [1, 2, 0, (3, 4, 5, 6), 7, 8],
        plurality: [0, 1, 2, (3, 4, 5, 6), 7, 8],
        bucklin: [1, 2, (3, 4, 5, 6), 7, 8, 0],
        borda: [1, 2, (3, 4, 5, 6), 7, 8, 0],
        minimax: [1, 2, (3, 4, 5, 6), 7, 8, 0],
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
        beatpath: ["Left", "Far Left", "Right", "Far Right"],
        river: ["Left", "Far Left", "Right", "Far Right"],
        instantrunoff: ["Left", "Right", "Far Left", "Far Right"],
        plurality: ["Right", "Left", "Far Left", "Far Right"],
        bucklin: [("Far Left", "Left"), ("Far Right", "Right")],
        borda: ["Left", "Right", "Far Left", "Far Right"],
        minimax: ["Left", "Far Left", "Right", "Far Right"],
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
        beatpath: ["Center", "Right", "Left"],
        river: ["Center", "Right", "Left"],
        instantrunoff: ["Right", "Left", "Center"],
        plurality: ["Right", "Left", "Center"],
        bucklin: ["Center", "Right", "Left"],
        borda: ["Center", "Right", "Left"],
        minimax: ["Center", "Right", "Left"],
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
        beatpath: ["Gore", "Bush", "Nader"],
        river: ["Gore", "Bush", "Nader"],
        instantrunoff: ["Bush", "Nader", "Gore"],
        plurality: ["Bush", "Nader", "Gore"],
        bucklin: ["Gore", "Nader", "Bush"],
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
        beatpath: ["A", "B", "C", "D"],
        river: ["A", "B", "C", "D"],
        instantrunoff: ["A", "D", "B", "C"],
        plurality: ["D", "A", "B", "C"],
        bucklin: ["C", ("A", "B"), "D"],
        borda: ["A", "C", "B", "D"],
        minimax: ["D", "A", "B", "C"],
    }

class ClonesTestCase(MethodTestCase):
    r'''Demonstration of the cloneproof Schwartz sequential dropping procdedure.
        http://fc.antioch.edu/~james_green-armytage/vm/survey.htm#beatpath
        
        Candidates R, S, and T are clones in a cycle, each tied with A.
        Ideally, A should tie with one of the clones.
    '''#"""#'''
    
    candidates = "ARST"
    
    ballots = [
        ("ARST", 3),
        ("ATRS", 2),
        ("ASTR", 1),
        ("STRA", 3),
        ("RSTA", 2),
        ("TRSA", 1),
    ]
    
    results = {
        rankedpairs: [("A", "R"), "S", "T"],
        beatpath: [("A", "R"), "S", "T"],
        river: [("A", "R"), "S", "T"],
        instantrunoff: ["A", ("R", "S"), "T"],
        plurality: ["A", "S", "R", "T"],
        bucklin: ["R", "S", "T", "A"],
        borda: [("R", "S"), "A", "T"],
        minimax: ["A", "R", "S", "T"],
    }

class BeatpathTestCase(MethodTestCase):
    r'''Demonstration of the difference between Beatpath and Ranked Pairs
        http://fc.antioch.edu/~james_green-armytage/vm/survey.htm#ranked_pairs
        
        In this case, the beatpath winner (A) would lose to the ranked pairs
        winner (B) in a head-to-head competition, but that loss is the weakest
        link in the B-A-D cycle.  River agrees with ranked pairs here.
    '''#"""#'''
    
    candidates = "ABCD"
    
    ballots = [
        ("BACD", 7),
        ("CDAB", 5),
        ("DBAC", 5),
        ("CADB", 4),
        ("BCAD", 4),
        ("DABC", 2),
        ("ADBC", 2),
        ("ACDB", 1),
    ]
    
    results = {
        rankedpairs: ["B", "A", "C", "D"],
        beatpath: ["A", "B", "C", "D"],
        river: ["B", "A", "C", "D"],
        instantrunoff: ["B", "C", "D", "A"],
        plurality: ["B", "C", "D", "A"],
        bucklin: [("A", "B"), ("C", "D")],
        borda: ["A", "B", "C", "D"],
        minimax: ["A", "B", "C", "D"],
    }

class PentagonTestCase(MethodTestCase):
    r'''Demonstration of the difference between Beatpath and Ranked Pairs
        http://fc.antioch.edu/~james_green-armytage/vm/survey.htm#ranked_pairs
        
        In this case, the ranked pairs winner (A) would lose to the beatpath
        winner (B) in a head-to-head competition, but that loss is the weakest
        link in the B-E-A cycle.
    '''#"""#'''
    
    candidates = "ABCDE"
    
    ballots = [
        ("BDEAC", 8),
        ("CABED", 8),
        ("EBADC", 8),
        ("EACBD", 5),
        ("DCBEA", 5),
        ("DACBE", 4),
        ("DCABE", 4),
        ("ABCDE", 3),
        ("EADCB", 3),
        ("CEBDA", 2),
        ("ABDCE", 2),
        ("DECAB", 1),
        ("BADCE", 1),
        ("ADCBE", 1),
        ("ECBAD", 1),
    ]
    
    results = {
        rankedpairs: ["B", "E", "A", "D", "C"],
        beatpath: ["A", "B", "D", "C", "E"],
        river: ["B", "E", "A", "D", "C"],
        instantrunoff: ["B", "E", "D", "C", "A"],
        plurality: ["E", "D", "C", "B", "A"],
        bucklin: ["A", "B", "C", "D", "E"],
        borda: [("A", "B"), "D", "E", "C"],
        minimax: ["A", "B", ("D", "E"), "C"],
    }

class WholeRunoffTestCase(MethodTestCase):
    r'''Differentiation between fractional and whole ER-IRV methods.
        http://fc.antioch.edu/~james_green-armytage/vm/survey.htm#erirv
        
        When equal rankings are allowed in instant runoff voting,
        you can either count each member of a first-place tie as a whole vote,
        or give each voter one vote to divide among them.
        In this case, whole votes would elect B, while fractional elects A.
        Does this mean that the whole method is better?
    '''#"""#'''
    
    candidates = "ABC"
    
    ballots = [
        (["A", "B", "C"], 41),
        (["B", "A", "C"], 10),
        (["B", "C", "A"], 4),
        ([("B", "C"), "A"], 30),
        (["C", "B", "A"], 15),
    ]
    
    results = {
        rankedpairs: ["B", "A", "C"],
        beatpath: ["B", "A", "C"],
        river: ["B", "A", "C"],
        instantrunoff: ["A", "C", "B"],
        plurality: ["A", "C", "B"],
        bucklin: ["B", "A", "C"],
        borda: ["B", "A", "C"],
        minimax: ["B", "A", "C"],
    }

class FractionalRunoffTestCase(MethodTestCase):
    r'''Differentiation between fractional and whole ER-IRV methods.
        In this case, whole votes would elect C, while fractional elects A.
        Does this mean that the fractional method is better?
    '''#"""#'''
    
    candidates = "ABCD"
    
    ballots = [
        (["A", "B", "C", "D"], 16),
        (["C", "A", "B", "D"], 33),
        (["B", "D", "A", "C"], 14),
        ([("B", "D"), "A", "C"], 16),
        ([("A", "D"), "B", "C"], 16),
    ]
    
    results = {
        rankedpairs: ["A", "B", "C", "D"],
        beatpath: ["A", "B", "C", "D"],
        river: ["A", "B", "C", "D"],
        instantrunoff: ["A", "C", "B", "D"],
        plurality: ["C", "A", "B", "D"],
        bucklin: ["A", ("B", "D"), "C"],
        borda: ["A", "B", "C", "D"],
        minimax: ["A", "B", "C", "D"],
    }

class IncompleteTestCase(MethodTestCase):
    r'''Incomplete ballots should not penalize unranked candidates.
        This criterion is more important in game design competitions
        than in political elections, though.
    '''#"""#'''
    
    candidates = "ABCDE"
    
    ballots = [
        (["A", "B", "C"], 4),
        (["B", "D", "E"], 4),
        (["C", "D", "B"], 3),
    ]
    
    results = {
        rankedpairs: ["A", "B", "C", "D", "E"],
        beatpath: ["A", "B", "C", "D", "E"],
        river: ["A", "B", "C", "D", "E"],
        instantrunoff: ["B", "A", "C", ("D", "E")],
        plurality: [("A", "B"), "C", ("D", "E")],
        bucklin: ["B", "D", "A", "C", "E"],
        borda: ["A", "B", "D", "C", "E"],
        minimax: ["A", "B", "C", "D", "E"],
    }

class RiverTestCase(MethodTestCase):
    r'''Demonstration of the difference between River and Ranked Pairs.
        http://web.archive.org/web/20071031155527/http://lists.electorama.com/pipermail/election-methods-electorama.com/2004-October/013971.html
        This is the CD>BD>DA>AC>AB>BC option.
    '''#"""#'''
    
    candidates = "ABCD"
    
    ballots = [
        ("BCDA", 8),
        ("BDAC", 5),
        ("CDAB", 5),
        ("ABCD", 4),
        ("ACBD", 4),
        ("ADCB", 3),
        ("CABD", 3),
        ("DACB", 3),
        ("ACDB", 2),
        ("BACD", 2),
        ("BADC", 2),
        ("BCAD", 2),
        ("CBDA", 2),
        ("CDBA", 2),
        ("DABC", 2),
        ("DBAC", 2),
        ("CADB", 1),
        ("DCAB", 1),
    ]
    
    results = {
        rankedpairs: ["B", "C", "D", "A"],
        beatpath: ["B", "C", "D", "A"],
        river: ["C", "D", "A", "B"],
        instantrunoff: ["A", "B", "C", "D"],
        plurality: ["B", ("A", "C"), "D"],
        bucklin: ["C", "B", "A", "D"],
        borda: ["C", "B", "A", "D"],
        minimax: ["B", "C", "D", "A"],
    }

class TiedTestCase(MethodTestCase):
    r'''Demonstration of an undecidable election.
        http://web.archive.org/web/20070220235817/http://cec.wustl.edu/~rhl1/rbvote/desc.html
        Todd definitely loses, but there is no fair way to choose between Ryan and Sara.
    '''#"""#'''
    
    candidates = ["Ryan", "Sara", "Todd"]
    
    ballots = [
        (["Ryan", "Sara", "Todd"], 25),
        (["Ryan", "Todd", "Sara"], 25),
        (["Sara", "Ryan", "Todd"], 25),
        (["Sara", "Todd", "Ryan"], 25),
    ]
    
    results = {
        rankedpairs: [("Ryan", "Sara"), "Todd"],
        beatpath: [("Ryan", "Sara"), "Todd"],
        river: [("Ryan", "Sara"), "Todd"],
        instantrunoff: [("Ryan", "Sara"), "Todd"],
        plurality: [("Ryan", "Sara"), "Todd"],
        bucklin: [("Ryan", "Sara"), "Todd"],
        borda: [("Ryan", "Sara"), "Todd"],
        minimax: [("Ryan", "Sara"), "Todd"],
    }

class RoShamBoTestCase(MethodTestCase):
    r'''Demonstration of a three-way tie.
        There is no fair way to let anyone win.
    '''#"""#'''
    
    candidates = ["Rock", "Paper", "Scissors"]
    
    ballots = [
        (["Rock", "Paper"], 25),
        (["Paper", "Scissors"], 25),
        (["Scissors", "Rock"], 25),
    ]
    
    results = {
        rankedpairs: [("Paper", "Rock", "Scissors")],
        beatpath: [("Paper", "Rock", "Scissors")],
        river: [("Paper", "Rock", "Scissors")],
        instantrunoff: [("Paper", "Rock", "Scissors")],
        plurality: [("Paper", "Rock", "Scissors")],
        bucklin: [("Paper", "Rock", "Scissors")],
        borda: [("Paper", "Rock", "Scissors")],
        minimax: [("Paper", "Rock", "Scissors")],
    }

class OctahedronTestCase(MethodTestCase):
    r'''Demonstration of a four-way tie between an obvious winner and loser.
    '''#"""#'''
    
    candidates = "ABCDEF"
    
    ballots = [
        ("ABCF", 25),
        ("ACDF", 25),
        ("ADEF", 25),
        ("AEBF", 25),
        ("BCDF", 10),
        ("CDEF", 10),
        ("DEBF", 10),
        ("EBCF", 10),
    ]
    
    results = {
        rankedpairs: ["A", ("B", "C", "D", "E"), "F"],
        beatpath: ["A", ("B", "C", "D", "E"), "F"],
        river: ["A", ("B", "C", "D", "E"), "F"],
        instantrunoff: ["A", ("B", "C", "D", "E"), "F"],
        plurality: ["A", ("B", "C", "D", "E"), "F"],
        bucklin: ["A", ("B", "C", "D", "E"), "F"],
        borda: ["A", ("B", "C", "D", "E"), "F"],
        minimax: ["A", ("B", "C", "D", "E"), "F"],
    }

class EqualWeightTestCase(MethodTestCase):
    r'''Demonstration of a partially cyclic graph where each edge has equal weight.
        Minimax produces unusual results here because it forgets relevant information.
        Bucklin produces unusual results here because no candidate is listed on a majority of ballots.
    '''#"""#'''
    
    candidates = "ABCDE"
    
    ballots = [
        ("AB", 10),
        ("AC", 10),
        ("AD", 10),
        ("BC", 10),
        ("CD", 10),
        ("DB", 10),
        ("BE", 10),
        ("CE", 10),
        ("DE", 10),
    ]
    
    results = {
        rankedpairs: ["A", ("B", "C", "D"), "E"],
        beatpath: ["A", ("B", "C", "D"), "E"],
        river: ["A", ("B", "C", "D"), "E"],
        instantrunoff: ["A", ("B", "C", "D"), "E"],
        plurality: ["A", ("B", "C", "D"), "E"],
        bucklin: [("A", "B", "C", "D", "E")],
        borda: ["A", ("B", "C", "D"), "E"],
        minimax: ["A", ("B", "C", "D", "E")],
    }


