r'''Ranked voting methods.
    Each method here is a function with two parameters:
        `votes` - A sequence of tuples.
            The first item is a list of candidate keys in ranked order;
            each item may be a tuple to indicate equal rankings.
            The second item is the number of times this sequence appears.
        `candidates` - A sequence of candidate keys.
            Keys in the vote rankings that don't appear in this list will be ignored.
'''#"""#'''

from __future__ import division
from collections import defaultdict

__all__ = []

def export(method):
    __all__.append(method.__name__)
    return method

def maybe_tuple(items):
    result = tuple(sorted(items))
    if len(result) == 1:
        result = result[0]
    return result

def unwind(ranks):
    for row in ranks:
        if isinstance(row, (tuple, set)):
            yield set(row)
        else:
            yield set([row])

class Graph(object):
    r'''Acyclic graph structure.
        Designed for use by the ranked pairs voting algorithm.
    '''#"""#'''
    
    def __init__(self, vertices):
        r'''Create a new Graph.
            `vertices` is a sequence of distinct hashable objects.
        '''#"""#'''
        # Store the inbound connections in a dictionary.
        # Outbound would make remove() easier, but roots() harder.
        self.vertices = dict((v, set()) for v in vertices)
    
    def edge(self, source, sink):
        r'''Create an edge from the source to the sink,
            as long as the graph remains acyclic.
            `source` and `sink` must be vertices.
            Returns whether the edge was created.
        '''#"""#'''
        connected = set([source])
        while connected:
            inbound = self.vertices[connected.pop()]
            if sink in inbound:
                return False
            connected.update(inbound)
        self.vertices[sink].add(source)
        return True
    
    def roots(self):
        r'''Collect the vertices with no inbound edges.
            These are the roots of the tree, or the best choices.
        '''#"""#'''
        return [key for key in self.vertices if not self.vertices[key]]
    
    def remove(self, vertex):
        r'''Remove a vertex from the graph.
        '''#"""#'''
        del self.vertices[vertex]
        for inbound in self.vertices.values():
            inbound.discard(vertex)
    
    def __nonzero__(self):
        r'''Truth value for the graph.
            A Graph is true if it contains any vertices.
        '''#"""#'''
        return bool(self.vertices)

@export
def rankedpairs(votes, candidates):
    # Tideman method, using a graph of preferences data.
    # Modified by ignoring unstated candidates, instead of
    # assuming that they're all worse than the ranked ones.
    comparisons = defaultdict(int)
    for ranks, count in votes:
        above = set()
        for row in unwind(ranks):
            for candidate in row:
                for former in above:
                    comparisons[former, candidate] += count
            above.update(row)
    
    # This seemingly-useless conversion avoids an error
    # caused by adding new items during iteration.
    comparisons = dict(comparisons)
    majorities = sorted((comparisons[a,b], comparisons.get((b,a), 0), a, b)
        for a,b in comparisons)
    
    graph = Graph(candidates)
    for major, minor, better, worse in reversed(majorities):
        if major > minor:
            result = graph.edge(better, worse)
    
    while graph:
        winners = graph.roots()
        yield maybe_tuple(winners)
        for item in winners:
            graph.remove(item)

@export
def instantrunoff(votes, candidates):
    # Instant Runoff Voting (IRV)
    # Modified to return a total ordering.
    candidates = set(candidates)
    majority = sum(item[1] for item in votes) / 2
    
    winners = []
    losers = []
    while candidates:
        totals = dict.fromkeys(candidates, 0)
        for ranks, count in votes:
            for row in unwind(ranks):
                possible = row & candidates
                if possible:
                    # Divide the votes evenly among the preferences.
                    value = count / len(possible)
                    for candidate in possible:
                        totals[candidate] += value
                    break
        
        counts = defaultdict(set)
        for key in totals:
            counts[totals[key]].add(key)
        
        top = max(counts)
        if top > majority:
            # We have a winner!
            found = counts[top]
            winners.append(maybe_tuple(found))
        else:
            # Eliminate the losers.
            found = counts[min(counts)]
            losers.insert(0, maybe_tuple(found))
        
        # Remove ranked candidates from the list
        candidates.difference_update(found)
    
    return winners + losers

@export
def plurality(votes, candidates):
    # First past the post, winner takes all.
    # Only the top preference is even looked at.
    totals = dict.fromkeys(candidates, 0)
    for ranks, count in votes:
        for row in unwind(ranks):
            value = count / len(row)
            for candidate in row:
                totals[candidate] += value
            break;
    
    counts = defaultdict(list)
    for key in totals:
        counts[totals[key]].append(key)
    
    result = sorted(counts)
    result.reverse()
    return [maybe_tuple(counts[total]) for total in result]

@export
def borda(votes, candidates):
    return []

@export
def modified_borda(votes, candidates):
    # A version of the Borda count that penalizes incomplete ballots.
    pass

@export
def bucklin(votes, candidates):
    pass

@export
def minimax(votes, candidates):
    pass

@export
def schulze(votes, candidates):
    pass

@export
def kemeny(votes, candidates):
    pass
