import sys
if sys.version<'2.4':
    # Python 2.3 disassembler is broken wrt co_lnotab; use a later version
    import _dis
    sys.modules['dis'] = _dis
    
def additional_tests():
    import doctest
    return doctest.DocFileSuite(
        'README.txt',
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE,
    )

