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
    r'''Basic graph structure.
        Designed for use by voting algorithms.
    '''#"""#'''
    
    def __init__(self, vertices):
        r'''Create a new Graph.
            `vertices` is a sequence of distinct hashable objects.
        '''#"""#'''
        # Store the inbound connections in a dictionary.
        # Outbound would make remove_vertex() easier, but roots() harder.
        self.vertices = dict((v, set()) for v in vertices)
    
    def edge(self, source, sink):
        r'''Create an edge from the source to the sink.
            This method provides no protections against cycles.
        '''#"""#'''
        self.vertices[sink].add(source)
        return True
    
    def acyclic_edge(self, source, sink):
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
    
    def edges(self):
        r'''Collect all edges in the graph.
        '''#"""#'''
        for sink in self.vertices:
            for source in self.vertices[sink]:
                yield source, sink
    
    def roots(self):
        r'''Collect the vertices with no inbound edges.
            These are the roots of the tree, or the best choices.
        '''#"""#'''
        return [key for key in self.vertices if not self.vertices[key]]
    
    def paths(self, source, sink):
        r'''Collect all paths from the source to the sink.
            Tends to yield shorter paths first.
        '''#"""#'''
        paths = [([sink], self.vertices[sink])]
        while paths:
            path, steps = paths.pop(0)
            for item in steps:
                if item == source:
                    yield [item] + path
                elif item not in path:
                    inbound = self.vertices[item]
                    if inbound:
                        paths.append(([item] + path, inbound))
    
    def remove_vertex(self, vertex):
        r'''Remove a vertex from the graph.
            Also removes any edges connected to that vertex.
        '''#"""#'''
        del self.vertices[vertex]
        for inbound in self.vertices.values():
            inbound.discard(vertex)
    
    def remove_edge(self, source, sink):
        r'''Remove an edge from the graph.
        '''#"""#'''
        self.vertices[sink].remove(source)
    
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
            result = graph.acyclic_edge(better, worse)
    
    while graph:
        winners = graph.roots()
        yield maybe_tuple(winners)
        for item in winners:
            graph.remove_vertex(item)

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
    # Borda Count method.
    # Unfortunately, this one penalizes unranked candidates.
    topval = len(candidates)
    ratings = dict.fromkeys(candidates, 0)
    for ranks, count in votes:
        value = topval
        for row in unwind(ranks):
            # Todo: Simplify this calculation.
            thisval = 0
            for c in row:
                value -= 1
                thisval += value
            thisval *= count
            thisval /= len(row)
            
            for candidate in row:
                ratings[candidate] += thisval
    
    counts = defaultdict(list)
    for key in ratings:
        counts[ratings[key]].append(key)
    return [maybe_tuple(counts[total]) for total in reversed(sorted(counts))]

@export
def modified_borda(votes, candidates):
    # A version of the Borda count that penalizes incomplete ballots.
    pass

@export
def bucklin(votes, candidates):
    # The Bucklin or Grand Junction voting system.
    # Seems to work well for three candidates, but not more.
    majority = sum(item[1] for item in votes) / 2
    print majority
    
    for n in range(1, len(candidates) + 1):
        totals = dict.fromkeys(candidates, 0)
        for ranks, count in votes:
            seen = 0
            for row in unwind(ranks):
                if len(row) > n - seen:
                    # Divide the votes evenly among the preferences.
                    # Letting each one count fully would let some ballots
                    # count more than others.
                    value = count * (n - seen) / len(row)
                else:
                    value = count
                
                for candidate in row:
                    totals[candidate] += value
                
                seen += len(row)
                if seen >= n:
                    break
        
        print totals
        counts = defaultdict(set)
        for key in totals:
            counts[totals[key]].add(key)
        
        print counts
        result = sorted(counts, reverse=True)
        print result
        if result[0] > majority:
            # We have a winner!
            return [maybe_tuple(counts[total]) for total in result]

@export
def minimax(votes, candidates):
    # Minimax / Successive reversal / Simpson method.
    # Using rankings, select unbeaten candidates.
    # If there aren't any, drop the weakest wins.
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
    graph = Graph(candidates)
    for a, b in comparisons:
        major = comparisons[a, b]
        minor = comparisons.get((b, a), 0)
        if major > minor:
            result = graph.edge(a, b)
    
    while graph:
        winners = graph.roots()
        if winners:
            yield maybe_tuple(winners)
            for item in winners:
                graph.remove_vertex(item)
        else:
            # This part could be optimized better.
            strength, sink, source = min((comparisons[a, b], a, b)
                for a, b in graph.edges())
            graph.remove_edge(sink, source)

@export
def beatpath(votes, candidates):
    # Schulze method, equivalent to Cloneproof Schwartz Sequential Dropping.
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
    graph = Graph(candidates)
    for a, b in comparisons:
        major = comparisons[a, b]
        minor = comparisons.get((b, a), 0)
        if major > minor:
            result = graph.edge(a, b)
    
    def path_steps(path):
        sequence = iter(path)
        prev = next(sequence)
        for item in sequence:
            yield prev, item
            prev = item
    
    def beat_strength(source, sink):
        # max() doesn't like empty iterables.
        strength = 0
        for path in graph.paths(source, sink):
            path_strength = min(comparisons.get(step, 0)
                for step in path_steps(path))
            if path_strength > strength:
                strength = path_strength
        return strength
    
    def pairs(sequence):
        r'''Yield each pair of the set exactly once.
            For example, if "A" and "B" are both in the set,
            yield either ("A", "B") or ("B", "A"), but not both.
        '''#"""#'''
        items = list(sequence)
        for b in xrange(1, len(items)):
            for a in xrange(0, b):
                yield items[a], items[b]
    
    final = Graph(candidates)
    for source, sink in pairs(candidates):
        major = beat_strength(sink, source)
        minor = beat_strength(source, sink)
        if major > minor:
            final.edge(sink, source)
        elif minor > major:
            final.edge(source, sink)
    
    while final:
        winners = final.roots()
        yield maybe_tuple(winners)
        for item in winners:
            final.remove_vertex(item)

@export
def river(votes, candidates):
    # A compromize between Beatpath and Ranked Pairs
    # http://web.archive.org/web/20071031155527/http://lists.electorama.com/pipermail/election-methods-electorama.com/2004-October/013971.html
    pass

