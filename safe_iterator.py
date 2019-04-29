
class endure:
    """Wraps an iterator to supply a `.remove_later()` method.

    Example: remove name out of list you're iterating over:
    >>> names = 'moritz harry edgar goofy dominik gorik'.split()
    >>> with endure(names) as safe_names:
    ...     for name in safe_names:
    ...         print(name)
    ...         if 'g' in name:
    ...             safe_names.remove_later()
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
    >>> with endure(numbers) as safe_numbers:
    ...     for n in safe_numbers:
    ...         print(1 / n)
    ...         safe_numbers.remove_later()
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
            def remove_later(me):
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


if __name__ == "__main__":
    import doctest
    doctest.testmod()

