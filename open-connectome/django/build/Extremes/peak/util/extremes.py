"""Production-quality "Min" and "Max" objects (adapted from PEP 326)"""

__all__ = ['Min', 'Max', 'Extreme']

class Extreme(object):     # Courtesy of PEP 326
    def __init__(self, cmpr, rep):
        object.__init__(self)
        self._cmpr = cmpr
        self._rep = rep

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return cmp(self._cmpr, other._cmpr)
        return self._cmpr

    def __repr__(self):
        return self._rep

    def __lt__(self,other):
        return self.__cmp__(other)<0

    def __le__(self,other):
        return self.__cmp__(other)<=0

    def __gt__(self,other):
        return self.__cmp__(other)>0

    def __eq__(self,other):
        return self.__cmp__(other)==0

    def __ge__(self,other):
        return self.__cmp__(other)>=0

    def __ne__(self,other):
        return self.__cmp__(other)<>0

Max = Extreme(1, "Max")
Min = Extreme(-1, "Min")



def additional_tests():
    import doctest
    return doctest.DocFileSuite(
        'README.txt', package='__main__',
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE,
    )




































