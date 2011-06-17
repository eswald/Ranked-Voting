r'''Utility functions and classes.
    Used by the ranked voting application, but not necessarily unique to it.
'''#"""#'''

def interleave(*sequences):
    sequences = map(iter, sequences)
    while sequences:
        for seq in sequences:
            yield seq.next()
