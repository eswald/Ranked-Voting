from collections import defaultdict

def _maybe_tuple(items):
    if len(items) == 1:
        return items[0]
    else:
        return tuple(items)

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

def rankedpairs(prefs):
    # Tideman method, using a graph of preferences data.
    # Modified by ignoring unstated candidates, instead of
    # assuming that they're all worse than the ranked ones.
    candidates = set()
    comparisons = defaultdict(int)
    for ranks, count in prefs:
        above = []
        for candidate in ranks:
            candidates.add(candidate)
            for former in above:
                comparisons[former, candidate] += count
            above.append(candidate)
    
    # This seemingly-useless conversion avoids an error
    # caused by adding new items during iteration.
    comparisons = dict(comparisons)
    majorities = sorted((comparisons[a,b], comparisons.get((b,a), 0), a, b)
        for a,b in comparisons)
    
    graph = Graph(candidates)
    for major, minor, better, worse in reversed(majorities):
        result = graph.edge(better, worse)
    
    while graph:
        winners = graph.roots()
        yield _maybe_tuple(winners)
        for item in winners:
            graph.remove(item)

def instantrunoff(prefs):
    pass

def plurality(prefs):
    # First past the post, winner takes all.
    # Only the top preference is even looked at.
    totals = defaultdict(int)
    for ranks, count in prefs:
        totals[ranks[0]] += count
        
        # Ensure that the other candidates make it into the result.
        for candidate in ranks[1:]:
            totals[candidate] += 0
    
    counts = defaultdict(list)
    for key in totals:
        counts[totals[key]].append(key)
    
    result = sorted(counts)
    result.reverse()
    return [_maybe_tuple(counts[total]) for total in result]

def borda(prefs):
    pass

def bucklin(prefs):
    pass

def minimax(prefs):
    pass

def schulze(prefs):
    pass

def kemeny(prefs):
    pass
