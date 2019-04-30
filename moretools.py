"""
Moretools. 
=====================

Useful tools beyond itertools. 

Inspired by `Alexander Schepanovski <https://github.com/Suor/funcy>`_.
"""
from contextlib import contextmanager
from itertools import *


def merge(*iterables):
    """Perform a n-way merge-sort on `iterables`.
    
    Examples:
    Merge ordered sequences:
    >>> list(merge([1,3,5], [2, 4, 6]))
    [1, 2, 3, 4, 5, 6]
    
    Perform 3-way merge on sequences of different length and type:
    >>> list(merge([7], (5, 6), range(1, 5)))
    [1, 2, 3, 4, 5, 6, 7]

    """
    iters = [iter(it) for it in iterables]
    store = [None] * len(iters)
    # fill store initially..
    for i, iterator in enumerate(iters):
        try:
            store[i] = next(iterator)
        except StopIteration:
            continue
    while None in store:
        store.remove(None)
    # enter the main loop..
    while iters:
        obj, i = min(((o, ix) for ix, o in enumerate(store)))
        try:
            store[i] = next(iters[i])
        except StopIteration:
            del store[i]
            del iters[i]
        yield obj


def pairs(iterable):
    """Draw pairs from `iterable` to yield items (n, n+1).

    Example:
    >>> list(pairs(range(5)))
    [(0, 1), (1, 2), (2, 3), (3, 4)]

    """
    it1, it2 = tee(iterable)
    next(it2)
    for a, b in zip(it1, it2):
        yield a, b


@contextmanager
def redirect(errstream=None):
    """Catch exceptions in the with-block and morph them into another.

    Examples:
    Change ValueError into KeyError:
    >>> with redirect():
    ...     raise ValueError

    >>> with redirect(errstream=print):
    ...     raise ValueError('value of 42 not feasible')
    ValueError: value of 42 not feasible

    """
    try:
        yield
    except Exception as exc:
        if errstream is not None:
            msg = "%s: %s" % (type(exc).__name__, str(exc))
            errstream(msg)


class remove_later:
    """Wraps an iterator to supply a `.remove_this()` method.

    Example: remove name out of list you're iterating over:
    >>> names = 'moritz harry edgar goofy dominik gorik'.split()
    >>> with remove_later(names) as safe_names:
    ...     for name in safe_names:
    ...         print(name)
    ...         if 'g' in name:
    ...             safe_names.remove_this()
    moritz
    harry
    edgar
    goofy
    dominik
    gorik
    >>> for name in names:
    ...     print(name)
    moritz
    harry
    dominik

    Elements are removed even if exception occured:
    >>> numbers = [-2, -1, 0, 1, 2, 3]
    >>> with remove_later(numbers) as safe_numbers:
    ...     for n in safe_numbers:
    ...         print(1 / n)
    ...         safe_numbers.remove_this()
    Traceback (most recent call last):
        ...
    ZeroDivisionError: division by zero
    >>> numbers
    [0, 1, 2, 3]

    """

    def __init__(self, iterable):
        class safe_iterator:
            pos = -1
            pending = [slice(0, 0)]
            def __init__(me, iterable):
                me.iterator = iter(iterable)
            def __iter__(me):
                return me
            def __next__(me):
                me.pos += 1
                return next(me.iterator)
            def remove_this(me):
                last = me.pending[-1]
                if me.pos - last.stop <= 0:
                    me.pending[-1] = slice(last.start, me.pos+1)
                else:
                    me.pending.append(slice(me.pos, me.pos+1))

        self.iterable = iterable
        self.safe_iterator = safe_iterator(iterable)

    def __enter__(self):
        return self.safe_iterator

    def __exit__(self, exc_type, exc, traceback):
        for i in reversed(self.safe_iterator.pending):
            del self.iterable[i]
        self.safe_iterator.pending.clear()


@contextmanager
def reraise(into=None, msg='', catch=None):
    """Catch exceptions in the with-block and morph them into another.

    Examples:
    Change ValueError into KeyError:
    >>> with reraise(KeyError, 'not in index'):
    ...     [1, 2, 3].index(17)
    Traceback (most recent call last):
        ...
    KeyError: 'not in index'

    Change the message only into something more meaningful:
    >>> with reraise(msg='42 seems not to be the answer to everything'):
    ...     [1, 2, 3].index(42)
    Traceback (most recent call last):
        ...
    ValueError: 42 seems not to be the answer to everything

    Catch only a certain exception-type:
    >>> with reraise(KeyError, catch=(IndexError, ZeroDivisionError)):
    ...     [1, 2, 3].index(17)
    Traceback (most recent call last):
        ...
    ValueError: 17 is not in list

    """
    try:
        yield
    except Exception as exc:
        if catch is not None and not isinstance(exc, catch):
            raise
        if into is None:
            into = type(exc)
        if msg:
            raise into(msg)
        raise into


if __name__ == "__main__":
    import doctest
    doctest.testmod()

