=======================================================
Generating Python Bytecode with ``peak.util.assembler``
=======================================================

``peak.util.assembler`` is a simple bytecode assembler module that handles most
low-level bytecode generation details like jump offsets, stack size tracking,
line number table generation, constant and variable name index tracking, etc.
That way, you can focus your attention on the desired semantics of your
bytecode instead of on these mechanical issues.

In addition to a low-level opcode-oriented API for directly generating specific
Python bytecodes, this module also offers an extensible mini-AST framework for
generating code from high-level specifications.  This framework does most of
the work needed to transform tree-like structures into linear bytecode
instructions, and includes the ability to do compile-time constant folding.

Please see the `BytecodeAssembler reference manual`_ for more details.

.. _BytecodeAssembler reference manual: http://peak.telecommunity.com/DevCenter/BytecodeAssembler#toc


Changes since version 0.5.2:

* Symbolic disassembly with full emulation of backward-compatible
  ``JUMP_IF_TRUE`` and ``JUMP_IF_FALSE`` opcodes on Python 2.7 -- tests now
  run clean on Python 2.7.

* Support for backward emulation of Python 2.7's ``JUMP_IF_TRUE_OR_POP`` and
  ``JUMP_IF_FALSE_OR_POP`` instructions on earlier Python versions; these
  emulations are also used in BytecodeAssembler's internal code generation,
  for maximum performance on 2.7+ (with no change to performance on older
  versions).

Changes since version 0.5.1:

* Initial support for Python 2.7's new opcodes and semantics changes, mostly
  by emulating older versions' behavior with macros.  (0.5.2 is really just
  a quick-fix release to allow packages using BytecodeAssembler to run on 2.7
  without having to change any of their code generation; future releases will
  provide proper support for the new and changed opcodes, as well as a test
  suite that doesn't show spurious differences in the disassembly listings
  under Python 2.7.)

Changes since version 0.5:

* Fix incorrect stack size calculation for ``MAKE_CLOSURE`` on Python 2.5+

Changes since version 0.3:

* New node types:

  * ``For(iterable, assign, body)`` -- define a "for" loop over `iterable`

  * ``UnpackSequence(nodes)`` -- unpacks a sequence that's ``len(nodes)`` long,
    and then generates the given nodes.

  * ``LocalAssign(name)`` -- issues a ``STORE_FAST``, ``STORE_DEREF`` or
    ``STORE_LOCAL`` as appropriate for the given name.

  * ``Function(body, name='<lambda>', args=(), var=None, kw=None, defaults=())``
    -- creates a nested function from `body` and puts it on the stack.

  * ``If(cond, then_, else_=Pass)`` -- "if" statement analogue

  * ``ListComp(body)`` and ``LCAppend(value)`` -- implement list comprehensions

  * ``YieldStmt(value)`` -- generates a ``YIELD_VALUE`` (plus a ``POP_TOP`` in
    Python 2.5+)

* ``Code`` objects are now iterable, yielding ``(offset, op, arg)`` triples,
  where `op` is numeric and `arg` is either numeric or ``None``.

* ``Code`` objects' ``.code()`` method can now take a "parent" ``Code`` object,
  to link the child code's free variables to cell variables in the parent.

* Added ``Code.from_spec()`` classmethod, that initializes a code object from a
  name and argument spec.

* ``Code`` objects now have a ``.nested(name, args, var, kw)`` method, that
  creates a child code object with the same ``co_filename`` and the supplied
  name/arg spec.

* Fixed incorrect stack tracking for the ``FOR_ITER`` and ``YIELD_VALUE``
  opcodes

* Ensure that ``CO_GENERATOR`` flag is set if ``YIELD_VALUE`` opcode is used

* Change tests so that Python 2.3's broken line number handling in ``dis.dis``
  and constant-folding optimizer don't generate spurious failures in this
  package's test suite.


Changes since version 0.2:

* Added ``Suite``, ``TryExcept``, and ``TryFinally`` node types

* Added a ``Getattr`` node type that does static or dynamic attribute access
  and constant folding

* Fixed ``code.from_function()`` not copying the ``co_filename`` attribute when
  ``copy_lineno`` was specified.

* The ``repr()`` of AST nodes doesn't include a trailing comma for 1-argument
  node types any more.

* Added a ``Pass`` symbol that generates no code, a ``Compare()`` node type
  that does n-way comparisons, and ``And()`` and ``Or()`` node types for doing
  logical operations.

* The ``COMPARE_OP()`` method now accepts operator strings like ``"<="``,
  ``"not in"``, ``"exception match"``, and so on, as well as numeric opcodes.
  See the standard library's ``opcode`` module for a complete list of the
  strings accepted (in the ``cmp_op`` tuple).  ``"<>"`` is also accepted as an
  alias for ``"!="``.

* Added code to verify that forward jump offsets don't exceed a 64KB span, and
  support absolute backward jumps to locations >64KB.

Changes since version 0.1:

* Constant handling has been fixed so that it doesn't confuse equal values of
  differing types (e.g. ``1.0`` and ``True``), or equal unhashable objects
  (e.g. two empty lists).

* Removed ``nil``, ``ast_curry()`` and ``folding_curry()``, replacing them with
  the ``nodetype()`` decorator and ``fold_args()``; please see the docs for
  more details.

* Added stack tracking across jumps, globally verifying stack level prediction
  consistency and automatically rejecting attempts to generate dead code.  It
  should now be virtually impossible to accidentally generate bytecode that can
  crash the interpreter.  (If you find a way, let me know!)

Changes since version 0.0.1:

* Added massive quantities of new documentation and examples

* Full block, loop, and closure support

* High-level functional code generation from trees, with smart labels and
  blocks, constant folding, extensibility, smart local variable names, etc.

* The ``.label()`` method was renamed to ``.here()`` to distinguish it from
  the new smart ``Label`` objects.

* Docs and tests were moved to README.txt instead of assembler.txt

* Added a demo that implements a "switch"-like statement template that shows
  how to extend the code generation system and how to abuse ``END_FINALLY``
  to implement a "computed goto" in bytecode.

* Various bug fixes

There are a few features that aren't tested yet, and not all opcodes may be
fully supported.  Also note the following limitations:

* Jumps to as-yet-undefined labels cannot span a distance greater than 65,535
  bytes.

* The ``dis()`` function in Python 2.3 has a bug that makes it show incorrect
  line numbers when the difference between two adjacent line numbers is
  greater than 255.  (To work around this, the test_suite uses a later version
  of ``dis()``, but do note that it may affect your own tests if you use
  ``dis()`` with Python 2.3 and use widely separated line numbers.)
  
If you find any other issues, please let me know.

Please also keep in mind that this is a work in progress, and the API may
change if I come up with a better way to do something.

Questions and discussion regarding this software should be directed to the
`PEAK Mailing List <http://www.eby-sarna.com/mailman/listinfo/peak>`_.

.. _toc:
.. contents:: **Table of Contents**


--------------
Programmer API
--------------


Code Objects
============

To generate bytecode, you create a ``Code`` instance and perform operations
on it.  For example, here we create a ``Code`` object representing lines
15 and 16 of some input source::

    >>> from peak.util.assembler import Code
    >>> c = Code()
    >>> c.set_lineno(15)   # set the current line number (optional)
    >>> c.LOAD_CONST(42)

    >>> c.set_lineno(16)   # set it as many times as you like
    >>> c.RETURN_VALUE()

You'll notice that most ``Code`` methods are named for a CPython bytecode
operation, but there also some other methods like ``.set_lineno()`` to let you
set the current line number.  There's also a ``.code()`` method that returns
a Python code object, representing the current state of the ``Code`` you've
generated::

    >>> from dis import dis
    >>> dis(c.code())
      15          0 LOAD_CONST               1 (42)
      16          3 RETURN_VALUE

As you can see, ``Code`` instances automatically generate a line number table
that maps each ``set_lineno()`` to the corresponding position in the bytecode.
    
And of course, the resulting code objects can be run with ``eval()`` or
``exec``, or used with ``new.function`` to create a function::

    >>> eval(c.code())
    42

    >>> exec c.code()   # exec discards the return value, so no output here

    >>> import new
    >>> f = new.function(c.code(), globals())
    >>> f()
    42

Finally, code objects are also iterable, yielding ``(offset, opcode, arg)``
tuples, where `arg` is ``None`` for opcodes with no arguments, and an integer
otherwise::

    >>> import peak.util.assembler as op
    >>> list(c) == [
    ...     (0, op.LOAD_CONST, 1),
    ...     (3, op.RETURN_VALUE, None)
    ... ]
    True

This can be useful for testing or otherwise inspecting code you've generated.


Symbolic Disassembler
=====================

Python's built-in disassembler can be verbose and hard to read when inspecting
complex generated code -- usually you don't care about bytecode offsets or
line numbers as much as you care about labels, for example.

So, BytecodeAssembler provides its own, simplified disassembler, which we'll
be using for more complex listings in this manual::

    >>> from peak.util.assembler import dump  

Some sample output, that also showcases some of BytecodeAssembler's
`High-Level Code Generation`_ features::

    >>> c = Code()
    >>> from peak.util.assembler import Compare, Local
    >>> c.return_(Compare(Local('a'), [('<', Local('b')), ('<', Local('c'))]))
    >>> dump(c.code())
                    LOAD_FAST                0 (a)
                    LOAD_FAST                1 (b)
                    DUP_TOP
                    ROT_THREE
                    COMPARE_OP               0 (<)
                    JUMP_IF_FALSE           L1
                    POP_TOP
                    LOAD_FAST                2 (c)
                    COMPARE_OP               0 (<)
                    JUMP_FORWARD            L2
            L1:     ROT_TWO
                    POP_TOP
            L2:     RETURN_VALUE

As you can see, the line numbers and bytecode offsets have been dropped,
making it esier to see where the jumps go.  (This also makes doctests more
robust against Python version changes, as ``dump()`` has some extra code to
make conditional jumps appear consistent across the major changes that were
made to conditional jump instructions between Python 2.6 and 2.7.)


Opcodes and Arguments
=====================

``Code`` objects have methods for all of CPython's symbolic opcodes.  Generally
speaking, each method accepts either zero or one argument, depending on whether
the opcode accepts an argument.

Python bytecode always encodes opcode arguments as 16 or 32-bit integers, but
sometimes these numbers are actually offsets into a sequence of names or
constants.  ``Code`` objects take care of maintaining these sequences for you,
allowing you to just pass in a name or value directly, instead of needing to
keep track of what numbers map to what names or values.

The name or value you pass in to such methods will be looked up in the
appropriate table (see `Code Attributes`_ below for a list), and if not found,
it will be added::

    >>> c = Code()
    >>> c.co_consts, c.co_varnames, c.co_names
    ([None], [], [])

    >>> c.LOAD_CONST(42)
    >>> c.LOAD_FAST('x')
    >>> c.LOAD_GLOBAL('y')
    >>> c.LOAD_NAME('z')

    >>> c.co_consts, c.co_varnames, c.co_names
    ([None, 42], ['x'], ['y', 'z'])

The one exception to this automatic addition feature is that opcodes referring
to "free" or "cell" variables will not automatically add new names, because the
names need to be defined first::

    >>> c.LOAD_DEREF('q')
    Traceback (most recent call last):
      ...
    NameError: ('Undefined free or cell var', 'q')

In general, opcode methods take the same arguments as their Python bytecode
equivalent.  But there are a few special cases.


Call Arguments
--------------

First, the ``CALL_FUNCTION()``, ``CALL_FUNCTION_VAR()``, ``CALL_FUNCTION_KW()``,
and ``CALL_FUNCTION_VAR_KW()`` methods all take *two* arguments, both of which
are optional.  (The ``_VAR`` and ``_KW`` suffixes in the method names indicate
whether or not a ``*args`` or ``**kwargs`` or both are also present on the
stack, in addition to the explicit positional and keyword arguments.)

The first argument of each of these methods, is the number of positional
arguments on the stack, and the second is the number of keyword/value pairs on
the stack (to be used as keyword arguments).  Both default to zero if not
supplied::

    >>> c = Code()
    >>> c.LOAD_CONST(type)
    >>> c.LOAD_CONST(27)
    >>> c.CALL_FUNCTION(1)      # 1 positional, no keywords
    >>> c.RETURN_VALUE()

    >>> eval(c.code())          # computes type(27)
    <type 'int'>

    >>> c = Code()
    >>> c.LOAD_CONST(dict)
    >>> c.LOAD_CONST('x')
    >>> c.LOAD_CONST(42)
    >>> c.CALL_FUNCTION(0,1)    # no positional, 1 keyword
    >>> c.RETURN_VALUE()

    >>> eval(c.code())          # computes dict(x=42)
    {'x': 42}


Jump Targets
------------

Opcodes that perform jumps or refer to addresses can be invoked in one of
two ways.  First, if you are jumping backwards (e.g. with ``JUMP_ABSOLUTE`` or
``CONTINUE_LOOP``), you can obtain the target bytecode offset using the
``.here()`` method, and then later pass that offset into the appropriate
method::

    >>> c = Code()
    >>> c.LOAD_CONST(42)
    >>> where = c.here()         # get a location near the start of the code
    >>> c.DUP_TOP()
    >>> c.POP_TOP()
    >>> c.JUMP_ABSOLUTE(where)   # now jump back to it

    >>> dump(c.code())
                    LOAD_CONST               1 (42)
            L1:     DUP_TOP
                    POP_TOP
                    JUMP_ABSOLUTE            L1

But if you are jumping *forward*, you will need to call the jump or setup
method without any arguments.  The return value will be a "forward reference"
object that can be called later to indicate that the desired jump target has
been reached::

    >>> c = Code()
    >>> c.LOAD_CONST(99)
    >>> forward = c.JUMP_IF_TRUE() # create a jump and a forward reference

    >>> c.LOAD_CONST(42)            # this is what we want to skip over
    >>> c.POP_TOP()

    >>> forward()   # calling the reference changes the jump to point here
    >>> c.LOAD_CONST(23)
    >>> c.RETURN_VALUE()

    >>> dump(c.code())
                    LOAD_CONST               1 (99)
                    JUMP_IF_TRUE             L1
                    LOAD_CONST               2 (42)
                    POP_TOP
            L1:     LOAD_CONST               3 (23)
                    RETURN_VALUE

    >>> eval(c.code())
    23


Other Special Opcodes
---------------------

The ``MAKE_CLOSURE`` method takes an argument for the number of default values
on the stack, just like the "real" Python opcode.  However, it also has an
an additional required argument: the number of closure cells on the stack.
The Python interpreter normally gets this number from a code object that's on
the stack, but ``Code`` objects need this value in order to update the
current stack size, for purposes of computing the required total stack size::

    >>> def x(a,b):     # a simple closure example
    ...     def y():
    ...         return a+b
    ...     return y

    >>> c = Code()
    >>> c.co_cellvars = ('a','b')

    >>> import sys
    >>> c.LOAD_CLOSURE('a')
    >>> c.LOAD_CLOSURE('b')
    >>> if sys.version>='2.5':
    ...     c.BUILD_TUPLE(2) # In Python 2.5+, free vars must be in a tuple
    >>> c.LOAD_CONST(None)   # in real code, this'd be a Python code constant
    >>> c.MAKE_CLOSURE(0,2)  # no defaults, 2 free vars in the new function

    >>> c.stack_size         # This will be 1, no matter what Python version
    1

The ``COMPARE_OP`` method takes an argument which can be a valid comparison
integer constant, or a string containing a Python operator, e.g.::

    >>> c = Code()
    >>> c.LOAD_CONST(1)
    >>> c.LOAD_CONST(2)
    >>> c.COMPARE_OP('not in')
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (1)
                  3 LOAD_CONST               2 (2)
                  6 COMPARE_OP               7 (not in)

The full list of valid operator strings can be found in the standard library's
``opcode`` module.  ``"<>"`` is also accepted as an alias for ``"!="``::

    >>> c.LOAD_CONST(3)
    >>> c.COMPARE_OP('<>')
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (1)
                  3 LOAD_CONST               2 (2)
                  6 COMPARE_OP               7 (not in)
                  9 LOAD_CONST               3 (3)
                 12 COMPARE_OP               3 (!=)


High-Level Code Generation
==========================

Typical real-life code generation use cases call for transforming tree-like
data structures into bytecode, rather than linearly outputting instructions.
``Code`` objects provide for this using a simple but high-level transformation
API.

``Code`` objects may be *called*, passing in one or more arguments.  Each
argument will have bytecode generated for it, according to its type:


Simple Constants
----------------

If an argument is an integer, long, float, complex, string, unicode, boolean,
``None``, or Python code object, it is treated as though it was passed to
the ``LOAD_CONST`` method directly::

    >>> c = Code()
    >>> c(1, 2L, 3.0, 4j+5, "6", u"7", False, None, c.code())
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (1)
                  3 LOAD_CONST               2 (2L)
                  6 LOAD_CONST               3 (3.0)
                  9 LOAD_CONST               4 ((5+4j))
                 12 LOAD_CONST               5 ('6')
                 15 LOAD_CONST               6 (u'7')
                 18 LOAD_CONST               7 (False)
                 21 LOAD_CONST               0 (None)
                 24 LOAD_CONST               8 (<code object <lambda> at ...>)

Note that although some values of different types may compare equal to each
other, ``Code`` objects will not substitute a value of a different type than
the one you requested::

    >>> c = Code()
    >>> c(1, True, 1.0, 1L)     # equal, but different types
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (1)
                  3 LOAD_CONST               2 (True)
                  6 LOAD_CONST               3 (1.0)
                  9 LOAD_CONST               4 (1L)

Simple Containers
-----------------

If an argument is a tuple, list, or dictionary, code is generated to
reconstruct the given data, recursively::

    >>> c = Code()
    >>> c({1:(2,"3"), 4:[5,6]})
    >>> dis(c.code())
      0           0 BUILD_MAP                0
                  3 DUP_TOP
                  4 LOAD_CONST               1 (1)
                  7 LOAD_CONST               2 (2)
                 10 LOAD_CONST               3 ('3')
                 13 BUILD_TUPLE              2
                 16 ROT_THREE
                 17 STORE_SUBSCR
                 18 DUP_TOP
                 19 LOAD_CONST               4 (4)
                 22 LOAD_CONST               5 (5)
                 25 LOAD_CONST               6 (6)
                 28 BUILD_LIST               2
                 31 ROT_THREE
                 32 STORE_SUBSCR


Arbitrary Constants
-------------------

The ``Const`` wrapper allows you to treat any object as a literal constant,
regardless of its type::

    >>> from peak.util.assembler import Const

    >>> c = Code()
    >>> c( Const( (1,2,3) ) )
    >>> dis(c.code())
      0           0 LOAD_CONST               1 ((1, 2, 3))

As you can see, the above creates code that references an actual tuple as
a constant, rather than generating code to recreate the tuple using a series of
``LOAD_CONST`` operations followed by a ``BUILD_TUPLE``.

If the value wrapped in a ``Const`` is not hashable, it is compared by identity
rather than value.  This prevents equal mutable values from being reused by
accident, e.g. if you plan to mutate the "constant" values later::

    >>> c = Code()
    >>> c(Const([]), Const([]))     # equal, but not the same object!
    >>> dis(c.code())
      0           0 LOAD_CONST               1 ([])
                  3 LOAD_CONST               2 ([])

Thus, although ``Const`` objects hash and compare based on equality for
hashable types::

    >>> hash(Const(3)) == hash(3)
    True
    >>> Const(3)==Const(3)
    True

They hash and compare based on object identity for non-hashable types::

    >>> c = Const([])
    >>> hash(c) == hash(id(c.value))
    True
    >>> c == Const(c.value)     # compares equal if same object
    True
    >>> c == Const([])          # but is not equal to a merely equal object
    False


``Suite`` and ``Pass``
----------------------

On occasion, it's helpful to be able to group a sequence of opcodes,
expressions, or statements together, to be passed as an argument to other node
types.  The ``Suite`` node type accomplishes this::

    >>> from peak.util.assembler import Suite, Pass

    >>> c = Code()
    >>> c.return_(Suite([Const(42), Code.DUP_TOP, Code.POP_TOP]))
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (42)
                  3 DUP_TOP
                  4 POP_TOP
                  5 RETURN_VALUE    

And ``Pass`` is a shortcut for an empty ``Suite``, that generates nothing::

    >>> Suite([])
    Pass

    >>> c = Code()
    >>> c(Pass)
    >>> c.return_(None)
    >>> dis(c.code())
      0           0 LOAD_CONST               0 (None)
                  3 RETURN_VALUE    


Local and Global Names
----------------------

The ``Local`` and ``Global`` wrappers take a name, and load either a local or
global variable, respectively::

    >>> from peak.util.assembler import Global, Local

    >>> c = Code()
    >>> c( Local('x'), Global('y') )
    >>> dis(c.code())
      0           0 LOAD_FAST                0 (x)
                  3 LOAD_GLOBAL              0 (y)

As with simple constants and ``Const`` wrappers, these objects can be used to
construct more complex expressions, like ``{a:(b,c)}``::

    >>> c = Code()
    >>> c( {Local('a'): (Local('b'), Local('c'))} )
    >>> dis(c.code())
      0           0 BUILD_MAP                0
                  3 DUP_TOP
                  4 LOAD_FAST                0 (a)
                  7 LOAD_FAST                1 (b)
                 10 LOAD_FAST                2 (c)
                 13 BUILD_TUPLE              2
                 16 ROT_THREE
                 17 STORE_SUBSCR

The ``LocalAssign`` node type takes a name, and stores a value in a local
variable::

    >>> from peak.util.assembler import LocalAssign
    >>> c = Code()
    >>> c(42, LocalAssign('x'))
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (42)
                  3 STORE_FAST               0 (x)

If the code object is not using "fast locals" (i.e. ``CO_OPTIMIZED`` isn't
set), local variables will be referenced using ``LOAD_NAME`` and ``STORE_NAME``
instead of ``LOAD_FAST`` and ``STORE_FAST``, and if the referenced local name
is a "cell" or "free" variable, ``LOAD_DEREF`` and ``STORE_DEREF`` are used
instead::

    >>> from peak.util.assembler import CO_OPTIMIZED
    >>> c = Code()
    >>> c.co_flags &= ~CO_OPTIMIZED
    >>> c.co_cellvars = ('y',)
    >>> c.co_freevars = ('z',)
    >>> c( Local('x'), Local('y'), Local('z') )
    >>> c( LocalAssign('x'), LocalAssign('y'), LocalAssign('z') )
    >>> dis(c.code())
      0           0 LOAD_NAME                0 (x)
                  3 LOAD_DEREF               0 (y)
                  6 LOAD_DEREF               1 (z)
                  9 STORE_NAME               0 (x)
                 12 STORE_DEREF              0 (y)
                 15 STORE_DEREF              1 (z)


Obtaining Attributes
--------------------

The ``Getattr`` node type takes an expression and an attribute name.  The
attribute name can be a constant string, in which case a ``LOAD_ATTR`` opcode
is used, and constant folding is done if possible::

    >>> from peak.util.assembler import Getattr

    >>> c = Code()
    >>> c(Getattr(Local('x'), '__class__'))
    >>> dis(c.code())
      0           0 LOAD_FAST                0 (x)
                  3 LOAD_ATTR                0 (__class__)


    >>> Getattr(Const(object), '__class__') # const expression, const result
    Const(<type 'type'>)

Or the attribute name can be an expression, in which case a ``getattr()`` call
is compiled instead::

    >>> c = Code()
    >>> c(Getattr(Local('x'), Local('y')))
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (<built-in function getattr>)
                  3 LOAD_FAST                0 (x)
                  6 LOAD_FAST                1 (y)
                  9 CALL_FUNCTION            2


Calling Functions and Methods
-----------------------------

    >>> from peak.util.assembler import Call

The ``Call`` wrapper takes 1-4 arguments: the expression to be called, a
sequence of positional arguments, a sequence of keyword/value pairs for
explicit keyword arguments, an "*" argument, and a "**" argument.  To omit any
of the optional arguments, just pass in an empty sequence in its place::

    >>> c = Code()
    >>> c( Call(Global('type'), [Const(27)]) )

    >>> dis(c.code())   # type(27)
      0           0 LOAD_GLOBAL              0 (type)
                  3 LOAD_CONST               1 (27)
                  6 CALL_FUNCTION            1

    >>> c = Code()
    >>> c(Call(Global('dict'), (), [('x', 42)]))

    >>> dis(c.code())   # dict(x=42)
      0           0 LOAD_GLOBAL              0 (dict)
                  3 LOAD_CONST               1 ('x')
                  6 LOAD_CONST               2 (42)
                  9 CALL_FUNCTION            256

    >>> c = Code()
    >>> c(Call(Global('foo'), (), (), Local('args'), Local('kw')))

    >>> dis(c.code())   # foo(*args, **kw)
      0           0 LOAD_GLOBAL              0 (foo)
                  3 LOAD_FAST                0 (args)
                  6 LOAD_FAST                1 (kw)
                  9 CALL_FUNCTION_VAR_KW     0


Returning Values
----------------

The ``Return(target)`` wrapper generates code for its target, followed by
a ``RETURN_VALUE`` opcode::

    >>> from peak.util.assembler import Return

    >>> c = Code()
    >>> c( Return(1) )
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (1)
                  3 RETURN_VALUE


``Code`` objects also have a ``return_()`` method that provides a more compact
spelling of the same thing::

    >>> c = Code()
    >>> c.return_((1,2))
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (1)
                  3 LOAD_CONST               2 (2)
                  6 BUILD_TUPLE              2
                  9 RETURN_VALUE

Both ``Return`` and ``return_()`` can be used with no argument, in which case
``None`` is returned::

    >>> c = Code()
    >>> c.return_()
    >>> dis(c.code())
      0           0 LOAD_CONST               0 (None)
                  3 RETURN_VALUE

    >>> c = Code()
    >>> c( Return() )
    >>> dis(c.code())
      0           0 LOAD_CONST               0 (None)
                  3 RETURN_VALUE


``If`` Conditions
-----------------

The ``If()`` node type generates conditional code, roughly equivalent to a
Python if/else statement::

    >>> from peak.util.assembler import If
    >>> c = Code()
    >>> c( If(Local('a'), Return(42), Return(55)) )
    >>> dump(c.code())
                    LOAD_FAST                0 (a)
                    JUMP_IF_FALSE            L1
                    POP_TOP
                    LOAD_CONST               1 (42)
                    RETURN_VALUE
            L1:     POP_TOP
                    LOAD_CONST               2 (55)
                    RETURN_VALUE

However, it can also be used like a Python 2.5+ conditional expression
(regardless of the targeted Python version)::

    >>> c = Code()
    >>> c( Return(If(Local('a'), 42, 55)) )
    >>> dump(c.code())
                    LOAD_FAST                0 (a)
                    JUMP_IF_FALSE            L1
                    POP_TOP
                    LOAD_CONST               1 (42)
                    JUMP_FORWARD             L2
            L1:     POP_TOP
                    LOAD_CONST               2 (55)
            L2:     RETURN_VALUE


Note that ``If()`` does *not* do constant-folding on its condition; even if the
condition is a constant, it will be tested at runtime.  This avoids issues with
using mutable constants, e.g.::

    >>> c = Code()
    >>> c(If(Const([]), 42, 55))
    >>> dump(c.code())
                    LOAD_CONST               1 ([])
                    JUMP_IF_FALSE            L1
                    POP_TOP
                    LOAD_CONST               2 (42)
                    JUMP_FORWARD             L2
            L1:     POP_TOP
                    LOAD_CONST               3 (55)


Labels and Jump Targets
-----------------------

The forward reference callbacks returned by jump operations are also usable
as code generation values, indicating that the jump should go to the
current location.  For example::

    >>> c = Code()
    >>> c.LOAD_CONST(99)
    >>> forward = c.JUMP_IF_FALSE()
    >>> c( 1, Code.POP_TOP, forward, Return(3) )
    >>> dump(c.code())
                    LOAD_CONST               1 (99)
                    JUMP_IF_FALSE            L1
                    LOAD_CONST               2 (1)
                    POP_TOP
            L1:     LOAD_CONST               3 (3)
                    RETURN_VALUE

However, there's an easier way to do the same thing, using ``Label`` objects::

    >>> from peak.util.assembler import Label
    >>> c = Code()
    >>> skip = Label()

    >>> c(99, skip.JUMP_IF_FALSE, 1, Code.POP_TOP, skip, Return(3))
    >>> dump(c.code())
                    LOAD_CONST               1 (99)
                    JUMP_IF_FALSE            L1
                    LOAD_CONST               2 (1)
                    POP_TOP
            L1:     LOAD_CONST               3 (3)
                    RETURN_VALUE

This approach has the advantage of being easy to use in complex trees.
``Label`` objects have attributes corresponding to every opcode that uses a
bytecode address argument.  Generating code for these attributes emits the
the corresponding opcode, and generating code for the label itself defines
where the previous opcodes will jump to.  Labels can have multiple jumps
targeting them, either before or after they are defined.  But they can't be
defined more than once::

    >>> c(skip)
    Traceback (most recent call last):
      ...
    AssertionError: Label previously defined


More Conditional Jump Instructions
----------------------------------

In Python 2.7, the traditional ``JUMP_IF_TRUE`` and ``JUMP_IF_FALSE``
instructions were replaced with four new instructions that either conditionally
or unconditionally pop the value being tested.  This was done to improve
performance, since virtually all conditional jumps in Python code pop the
value on one branch or the other.

To provide better cross-version compatibility, BytecodeAssembler emulates the
old instructions on Python 2.7 by emitting a ``DUP_TOP`` followed by a
``POP_JUMP_IF_FALSE`` or ``POP_JUMP_IF_TRUE`` instruction.

However, since this decreases performance, BytecodeAssembler *also* emulates
Python 2.7's ``JUMP_IF_FALSE_OR_POP`` and ``JUMP_IF_FALSE_OR_TRUE`` opcodes
on *older* Pythons::

    >>> c = Code()
    >>> l1, l2 = Label(), Label()
    >>> c(Local('a'), l1.JUMP_IF_FALSE_OR_POP, Return(27), l1)
    >>> c(l2.JUMP_IF_TRUE_OR_POP, Return(42), l2, Code.RETURN_VALUE)
    >>> dump(c.code())
                    LOAD_FAST                0 (a)
                    JUMP_IF_FALSE           L1
                    POP_TOP
                    LOAD_CONST               1 (27)
                    RETURN_VALUE   
            L1:     JUMP_IF_TRUE            L2
                    POP_TOP
                    LOAD_CONST               2 (42)
                    RETURN_VALUE
            L2:     RETURN_VALUE

This means that you can immediately begin using the "or-pop" variations, in
place of a jump followed by a pop, and BytecodeAssembler will use the faster
single instruction automatically on Python 2.7+.

BytecodeAssembler *also* supports using Python 2.7's conditional jumps
that do unconditional pops, but currently cannot emulate them on older Python
versions, so at the moment you should use them only when your code requires
Python 2.7.

(Note: for ease in doctesting across Python versions, the ``dump()`` function
*always* shows the code as if it were generated for Python 2.6 or lower, so
if you need to check the *actual* bytecodes generated, you must use Python's
``dis.dis()`` function instead!)


N-Way Comparisons
-----------------

You can generate N-way comparisons using the ``Compare()`` node type::

    >>> from peak.util.assembler import Compare

    >>> c = Code()
    >>> c(Compare(Local('a'), [('<', Local('b'))]))
    >>> dis(c.code())
      0           0 LOAD_FAST                0 (a)
                  3 LOAD_FAST                1 (b)
                  6 COMPARE_OP               0 (<)

3-way comparisons generate code that's a bit more complex.  Here's a three-way
comparison (``a<b<c``)::

    >>> c = Code()
    >>> c.return_(Compare(Local('a'), [('<', Local('b')), ('<', Local('c'))]))
    >>> dump(c.code())
                    LOAD_FAST                0 (a)
                    LOAD_FAST                1 (b)
                    DUP_TOP
                    ROT_THREE
                    COMPARE_OP               0 (<)
                    JUMP_IF_FALSE           L1
                    POP_TOP
                    LOAD_FAST                2 (c)
                    COMPARE_OP               0 (<)
                    JUMP_FORWARD            L2
            L1:     ROT_TWO
                    POP_TOP
            L2:     RETURN_VALUE

And a four-way (``a<b>c!=d``)::

    >>> c = Code()
    >>> c.return_(
    ...     Compare( Local('a'), [
    ...         ('<', Local('b')), ('>', Local('c')), ('!=', Local('d'))
    ...     ])
    ... )
    >>> dump(c.code())
                    LOAD_FAST                0 (a)
                    LOAD_FAST                1 (b)
                    DUP_TOP
                    ROT_THREE
                    COMPARE_OP               0 (<)
                    JUMP_IF_FALSE           L1
                    POP_TOP
                    LOAD_FAST                2 (c)
                    DUP_TOP
                    ROT_THREE
                    COMPARE_OP               4 (>)
                    JUMP_IF_FALSE           L1
                    POP_TOP
                    LOAD_FAST                3 (d)
                    COMPARE_OP               3 (!=)
                    JUMP_FORWARD            L2
            L1:     ROT_TWO
                    POP_TOP
            L2:     RETURN_VALUE


Sequence Unpacking
------------------

The ``UnpackSequence`` node type takes a sequence of code generation targets,
and generates an ``UNPACK_SEQUENCE`` of the correct length, followed by the
targets::

    >>> from peak.util.assembler import UnpackSequence
    >>> c = Code()  
    >>> c((1,2), UnpackSequence([LocalAssign('x'), LocalAssign('y')]))
    >>> dis(c.code())   # x, y = 1, 2
      0           0 LOAD_CONST               1 (1)
                  3 LOAD_CONST               2 (2)
                  6 BUILD_TUPLE              2
                  9 UNPACK_SEQUENCE          2
                 12 STORE_FAST               0 (x)
                 15 STORE_FAST               1 (y)


Yield Statements
----------------

The ``YieldStmt`` node type generates the necessary opcode(s) for a ``yield``
statement, based on the target Python version.  (In Python 2.5+, a ``POP_TOP``
must be generated after a ``YIELD_VALUE`` in order to create a yield statement,
as opposed to a yield expression.)  It also sets the code flags needed to make
the resulting code object a generator::

    >>> from peak.util.assembler import YieldStmt
    >>> c = Code()
    >>> c(YieldStmt(1), YieldStmt(2), Return(None))
    >>> list(eval(c.code()))
    [1, 2]



Constant Detection and Folding
==============================

The ``const_value()`` function can be used to check if an expression tree has
a constant value, and to obtain that value.  Simple constants are returned
as-is::

    >>> from peak.util.assembler import const_value

    >>> simple_values = [1, 2L, 3.0, 4j+5, "6", u"7", False, None, c.code()]

    >>> map(const_value, simple_values)
    [1, 2L, 3.0, (5+4j), '6', u'7', False, None, <code object <lambda> ...>]

Values wrapped in a ``Const()`` are also returned as-is::

    >>> map(const_value, map(Const, simple_values))
    [1, 2L, 3.0, (5+4j), '6', u'7', False, None, <code object <lambda> ...>]

But no other node types produce constant values; instead, ``NotAConstant`` is
raised::

    >>> const_value(Local('x'))
    Traceback (most recent call last):
      ...
    NotAConstant: Local('x')

Tuples of constants are recursively replaced by constant tuples::

    >>> const_value( (1,2) )
    (1, 2)

    >>> const_value( (1, (2, Const(3))) )
    (1, (2, 3))

But any non-constant values anywhere in the structure cause an error::

    >>> const_value( (1,Global('y')) )
    Traceback (most recent call last):
      ...
    NotAConstant: Global('y')

As do any types not previously described here::

    >>> const_value([1,2])
    Traceback (most recent call last):
      ...
    NotAConstant: [1, 2]

Unless of course they're wrapped with ``Const``::

    >>> const_value(Const([1,2]))
    [1, 2]


Folding Function Calls
----------------------

The ``Call`` wrapper can also do simple constant folding, if all of its input
parameters are constants.  (Actually, the `args` and `kwargs` arguments must be
*sequences* of constants and 2-tuples of constants, respectively.)

If a ``Call`` can thus compute its value in advance, it does so, returning a
``Const`` node instead of a ``Call`` node::

    >>> Call( Const(type), [1] )
    Const(<type 'int'>)

Thus, you can also take the ``const_value()`` of such calls::

    >>> const_value( Call( Const(dict), [], [('x',27)] ) )
    {'x': 27}

Which means that constant folding can propagate up an AST if the result is
passed in to another ``Call``::

    >>> Call(Const(type), [Call( Const(dict), [], [('x',27)] )])
    Const(<type 'dict'>)

Notice that this folding takes place eagerly, during AST construction.  If you
want to implement delayed folding after constant propagation or variable
substitution, you'll need to recreate the tree, or use your own custom AST
types.  (See `Custom Code Generation`_, below.)

Note that you can disable folding using the ``fold=False`` keyword argument to
``Call``, if you want to ensure that even compile-time constants are computed
at runtime.  Compare::

    >>> c = Code()
    >>> c( Call(Const(type), [1]) )
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (<type 'int'>)

    >>> c = Code()
    >>> c( Call(Const(type), [1], fold=False) )
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (<type 'type'>)
                  3 LOAD_CONST               2 (1)
                  6 CALL_FUNCTION            1

Folding is also *automatically* disabled for calls with no arguments of any
kind (such as ``globals()`` or ``locals()``), whose values are much more likely
to change dynamically at runtime::

    >>> c = Code()
    >>> c( Call(Const(locals)) )
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (<built-in function locals>)
                  3 CALL_FUNCTION            0

Note, however, that folding is disabled for *any* zero-argument call,
regardless of the thing being called.  It is not specific to ``locals()`` and
``globals()``, in other words.


Logical And/Or
--------------

You can evaluate logical and/or expressions using the ``And`` and ``Or`` node
types::

    >>> from peak.util.assembler import And, Or

    >>> c = Code()
    >>> c.return_( And([Local('x'), Local('y')]) )
    >>> dump(c.code())
                    LOAD_FAST                0 (x)
                    JUMP_IF_FALSE           L1        
                    POP_TOP
                    LOAD_FAST                1 (y)
            L1:     RETURN_VALUE

    >>> c = Code()
    >>> c.return_( Or([Local('x'), Local('y')]) )
    >>> dump(c.code())
                    LOAD_FAST                0 (x)
                    JUMP_IF_TRUE            L1
                    POP_TOP
                    LOAD_FAST                1 (y)
            L1:     RETURN_VALUE


True or false constants are folded automatically, avoiding code generation
for intermediate values that will never be used in the result::

    >>> c = Code()
    >>> c.return_( And([1, 2, Local('y')]) )
    >>> dis(c.code())
      0           0 LOAD_FAST                0 (y)
                  3 RETURN_VALUE

    >>> c = Code()
    >>> c.return_( And([1, 2, Local('y'), 0]) )
    >>> dump(c.code())
                    LOAD_FAST                0 (y)
                    JUMP_IF_FALSE           L1
                    POP_TOP
                    LOAD_CONST               1 (0)
            L1:     RETURN_VALUE

    >>> c = Code()
    >>> c.return_( Or([1, 2, Local('y')]) )
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (1)
                  3 RETURN_VALUE

    >>> c = Code()
    >>> c.return_( Or([False, Local('y'), 3]) )
    >>> dump(c.code())
                    LOAD_FAST                0 (y)
                    JUMP_IF_TRUE            L1
                    POP_TOP
                    LOAD_CONST               1 (3)
            L1:     RETURN_VALUE


Custom Code Generation
======================

Code generation is extensible: you can use any callable as a code-generation
target.  It will be called with exactly one argument: the code object.  It can
then perform whatever operations are desired.

In the most trivial case, you can use any unbound ``Code`` method as a code
generation target, e.g.::

    >>> c = Code()
    >>> c.LOAD_GLOBAL('foo')
    >>> c(Call(Code.DUP_TOP, ()))
    >>> dis(c.code())
      0           0 LOAD_GLOBAL              0 (foo)
                  3 DUP_TOP
                  4 CALL_FUNCTION            0

As you can see, the ``Code.DUP_TOP()`` is called on the code instance, causing
a ``DUP_TOP`` opcode to be output.  This is sometimes a handy trick for
accessing values that are already on the stack.  More commonly, however, you'll
want to implement more sophisticated callables.

To make it easy to create diverse target types, a ``nodetype()`` decorator is
provided::

    >>> from peak.util.assembler import nodetype

It allows you to create code generation target types using functions.  Your
function should take one or more arguments, with a ``code=None`` optional
argument in the last position.  It should check whether ``code is None`` when
called, and if so, return a tuple of the preceding arguments.  If ``code``
is not ``None``, then it should do whatever code generating tasks are required.
For example::

    >>> def TryFinally(block1, block2, code=None):
    ...     if code is None:
    ...         return block1, block2
    ...     code(
    ...         Code.SETUP_FINALLY,
    ...             block1,
    ...         Code.POP_BLOCK,
    ...             block2,
    ...         Code.END_FINALLY
    ...     )
    >>> TryFinally = nodetype()(TryFinally)

Note: although the nodetype() generator can be used above the function
definition in either Python 2.3 or 2.4, it cannot be done in a doctest under
Python 2.3, so this document doesn't attempt to demonstrate that.  Under
2.4, you would do something like this::

    @nodetype()
    def TryFinally(...):

and code that needs to also work under 2.3 should do something like this::

    nodetype()
    def TryFinally(...):

But to keep the examples here working with doctest, we'll be doing our
``nodetype()`` calls after the end of the function definitions, e.g.::

    >>> def ExprStmt(value, code=None):
    ...     if code is None:
    ...         return value,
    ...     code( value, Code.POP_TOP )
    >>> ExprStmt = nodetype()(ExprStmt)

    >>> c = Code()
    >>> c( TryFinally(ExprStmt(1), ExprStmt(2)) )
    >>> dump(c.code())
                    SETUP_FINALLY           L1
                    LOAD_CONST               1 (1)
                    POP_TOP
                    POP_BLOCK
                    LOAD_CONST               0 (None)
            L1:     LOAD_CONST               2 (2)
                    POP_TOP
                    END_FINALLY

The ``nodetype()`` decorator is virtually identical to the ``struct()``
decorator in the DecoratorTools package, except that it does not support
``*args``, does not create a field for the ``code`` argument, and generates a
``__call__()`` method that reinvokes the wrapped function to do the actual
code generation.

Among the benefits of this decorator are:

* It gives your node types a great debugging format::

    >>> tf = TryFinally(ExprStmt(1), ExprStmt(2))
    >>> tf
    TryFinally(ExprStmt(1), ExprStmt(2))

* It makes named fields accessible::

    >>> tf.block1
    ExprStmt(1)

    >>> tf.block2
    ExprStmt(2)

* Hashing and comparison work as expected (handy for algorithms that require
  comparing or caching AST subtrees, such as common subexpression
  elimination)::

    >>> ExprStmt(1) == ExprStmt(1)
    True
    >>> ExprStmt(1) == ExprStmt(2)
    False


Please see the `struct decorator documentation`_ for info on how to customize
node types further.

.. _struct decorator documentation: http://peak.telecommunity.com/DevCenter/DecoratorTools#the-struct-decorator

Note: hashing only works if all the values you return in your argument tuple
are hashable, so you should try to convert them if possible.  For example, if
an argument accepts any sequence, you should probably convert it to a tuple
before returning it.  Most of the examples in this document, and the node types
supplied by ``peak.util.assembler`` itself do this.


Constant Folding in Custom Targets
----------------------------------

If you want to incorporate constant-folding into your AST nodes, you can do
so by checking for constant values and folding them at either construction
or code generation time.  For example, this ``And`` node type (a simpler
version of the one included in ``peak.util.assembler``) folds constants during
code generation, by not generating unnecessary branches when it can
prove which way a branch will go::

    >>> from peak.util.assembler import NotAConstant

    >>> def And(values, code=None):
    ...     if code is None:
    ...         return tuple(values),
    ...     end = Label()
    ...     for value in values[:-1]:
    ...         try:
    ...             if const_value(value):
    ...                 continue        # true constants can be skipped
    ...         except NotAConstant:    # but non-constants require code
    ...             code(value, end.JUMP_IF_FALSE_OR_POP)
    ...         else:       # and false constants end the chain right away
    ...             return code(value, end)
    ...     code(values[-1], end)
    >>> And = nodetype()(And)

    >>> c = Code()
    >>> c.return_( And([1, 2]) )
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (2)
                  3 RETURN_VALUE

    >>> c = Code()
    >>> c.return_( And([1, 2, Local('x')]) )
    >>> dis(c.code())
      0           0 LOAD_FAST                0 (x)
                  3 RETURN_VALUE

    >>> c = Code()
    >>> c.return_( And([Local('x'), False, 27]) )
    >>> dump(c.code())
                    LOAD_FAST                0 (x)
                    JUMP_IF_FALSE           L1
                    POP_TOP
                    LOAD_CONST               1 (False)
            L1:     RETURN_VALUE

The above example only folds constants at code generation time, however.  You
can also do constant folding at AST construction time, using the
``fold_args()`` function.  For example::

    >>> from peak.util.assembler import fold_args

    >>> def Getattr(ob, name, code=None):
    ...     try:
    ...         name = const_value(name)
    ...     except NotAConstant:
    ...         return Call(Const(getattr), [ob, name])
    ...     if code is None:
    ...         return fold_args(Getattr, ob, name)
    ...     code(ob)
    ...     code.LOAD_ATTR(name)
    >>> Getattr = nodetype()(Getattr)

    >>> const_value(Getattr(1, '__class__'))
    <type 'int'>

The ``fold_args()`` function tries to evaluate the node immediately, if all of
its arguments are constants, by creating a temporary ``Code`` object, and
running the supplied function against it, then doing an ``eval()`` on the
generated code and wrapping the result in a ``Const``.  However, if any of the
arguments are non-constant, the original arguments (less the function) are
returned. This causes a normal node instance to be created instead of a
``Const``.

This isn't a very *fast* way of doing partial evaluation, but it makes it
really easy to define new code generation targets without writing custom
constant-folding code for each one.  Just ``return fold_args(ThisType, *args)``
instead of ``return args``, if you want your node constructor to be able to do
eager evaluation.  If you need to, you can check your parameters in order to
decide whether to call ``fold_args()`` or not; this is in fact how ``Call``
implements its ``fold`` argument and the suppression of folding when
the call has no arguments.

(By the way, this same ``Getattr`` node type is also available


Setting the Code's Calling Signature
====================================

The simplest way to set up the calling signature for a ``Code`` instance is
to clone an existing function or code object's signature, using the
``Code.from_function()`` or ``Code.from_code()`` classmethods.  These methods
create a new ``Code`` instance whose calling signature (number and names of
arguments) matches that of the original function or code objects::

    >>> def f1(a,b,*c,**d):
    ...     pass

    >>> c = Code.from_function(f1)
    >>> f2 = new.function(c.code(), globals())

    >>> import inspect

    >>> tuple(inspect.getargspec(f1))
    (['a', 'b'], 'c', 'd', None)

    >>> tuple(inspect.getargspec(f2))
    (['a', 'b'], 'c', 'd', None)

Note that these constructors do not copy any actual *code* from the code
or function objects.  They simply copy the signature, and, if you set the
``copy_lineno`` keyword argument to a true value, they will also set the
created code object's ``co_firstlineno`` to match that of the original code or
function object::

    >>> c1 = Code.from_function(f1, copy_lineno=True)
    >>> c1.co_firstlineno
    1
    >>> c1.co_filename is f1.func_code.co_filename
    True

If you create a ``Code`` instance from a function that has nested positional
arguments, the returned code object will include a prologue to unpack the
arguments properly::

    >>> def f3(a, (b,c), (d,(e,f))):
    ...     pass

    >>> f4 = new.function(Code.from_function(f3).code(), globals())
    >>> dis(f4)
      0           0 LOAD_FAST                1 (.1)
                  3 UNPACK_SEQUENCE          2
                  6 STORE_FAST               3 (b)
                  9 STORE_FAST               4 (c)
                 12 LOAD_FAST                2 (.2)
                 15 UNPACK_SEQUENCE          2
                 18 STORE_FAST               5 (d)
                 21 UNPACK_SEQUENCE          2
                 24 STORE_FAST               6 (e)
                 27 STORE_FAST               7 (f)

This is roughly the same code that Python would generate to do the same
unpacking process, and is designed so that the ``inspect`` module will
recognize it as an argument unpacking prologue::

    >>> tuple(inspect.getargspec(f3))
    (['a', ['b', 'c'], ['d', ['e', 'f']]], None, None, None)

    >>> tuple(inspect.getargspec(f4))
    (['a', ['b', 'c'], ['d', ['e', 'f']]], None, None, None)

You can also use the ``from_spec(name='<lambda>', args=(), var=None, kw=None)``
classmethod to explicitly set a name and argument spec for a new code object::

    >>> c = Code.from_spec('a', ('b', ('c','d'), 'e'), 'f', 'g')
    >>> c.co_name
    'a'

    >>> c.co_varnames
    ['b', '.1', 'e', 'f', 'g', 'c', 'd']

    >>> c.co_argcount
    3
    
    >>> tuple(inspect.getargs(c.code()))
    (['b', ['c', 'd'], 'e'], 'f', 'g')


Code Attributes
===============

``Code`` instances have a variety of attributes corresponding to either the
attributes of the Python code objects they generate, or to the current state
of code generation.

For example, the ``co_argcount`` and ``co_varnames`` attributes
correspond to those used in creating the code for a Python function.  If you
want your code to be a function, you can set them as follows::

    >>> c = Code()
    >>> c.co_argcount = 3
    >>> c.co_varnames = ['a','b','c']

    >>> c.LOAD_CONST(42)
    >>> c.RETURN_VALUE()

    >>> f = new.function(c.code(), globals())
    >>> f(1,2,3)
    42

    >>> import inspect
    >>> tuple(inspect.getargspec(f))
    (['a', 'b', 'c'], None, None, None)

Although Python code objects want ``co_varnames`` to be a tuple, ``Code``
instances use a list, so that names can be added during code generation.  The
``.code()`` method automatically creates tuples where necessary.

Here are all of the ``Code`` attributes you may want to read or write:

co_filename
    A string representing the source filename for this code.  If it's an actual
    filename, then tracebacks that pass through the generated code will display
    lines from the file.  The default value is ``'<generated code>'``.

co_name
    The name of the function, class, or other block that this code represents.
    The default value is ``'<lambda>'``.

co_argcount
    Number of positional arguments a function accepts; defaults to 0

co_varnames
    A list of strings naming the code's local variables, beginning with its
    positional argument names, followed by its ``*`` and ``**`` argument names,
    if applicable, followed by any other local variable names.  These names
    are used by the ``LOAD_FAST`` and ``STORE_FAST`` opcodes, and invoking
    the ``.LOAD_FAST(name)`` and ``.STORE_FAST(name)`` methods of a code object
    will automatically add the given name to this list, if it's not already
    present.

co_flags
    The flags for the Python code object.  This defaults to
    ``CO_OPTIMIZED | CO_NEWLOCALS``, which is the correct value for a function
    using "fast" locals.  This value is automatically or-ed with ``CO_NOFREE``
    when generating a code object, if the ``co_cellvars`` and ``co_freevars``
    attributes are empty.  And if you use the ``LOAD_NAME()``,
    ``STORE_NAME()``, or ``DELETE_NAME()`` methods, the ``CO_OPTIMIZED`` bit
    is automatically reset, since these opcodes can only be used when the
    code is running with a real (i.e. not virtualized) ``locals()`` dictionary.

    If you need to change any other flag bits besides the above, you'll need to
    set or clear them manually.  For your convenience, the
    ``peak.util.assembler`` module exports all the ``CO_`` constants used by
    Python.  For example, you can use ``CO_VARARGS`` and ``CO_VARKEYWORDS`` to
    indicate whether a function accepts ``*`` or ``**`` arguments, as long as
    you extend the ``co_varnames`` list accordingly.  (Assuming you don't have
    an existing function or code object with the desired signature, in which
    case you could just use the ``from_function()`` or ``from_code()``
    classmethods instead of messing with these low-level attributes and flags.)

stack_size
    The predicted height of the runtime value stack, as of the current opcode.
    Its value is automatically updated by most opcodes, but if you are doing
    something sufficiently tricky (as in the ``Switch`` demo, below) you may
    need to explicitly set it.

    The ``stack_size`` automatically becomes ``None`` after any unconditional
    jump operations, such as ``JUMP_FORWARD``, ``BREAK_LOOP``, or
    ``RETURN_VALUE``.  When the stack size is ``None``, the only operations
    that can be performed are the resolving of forward references (which will
    set the stack size to what it was when the reference was created), or
    manually setting the stack size.

co_freevars
    A tuple of strings naming a function's "free" variables.  Defaults to an
    empty tuple.  A function's free variables are the variables it "inherits"
    from its surrounding scope.  If you're going to use this, you should set
    it only once, before generating any code that references any free *or* cell
    variables.

co_cellvars
    A tuple of strings naming a function's "cell" variables.  Defaults to an
    empty tuple.  A function's cell variables are the variables that are
    "inherited" by one or more of its nested functions.  If you're going to use
    this, you should set it only once, before generating any code that
    references any free *or* cell variables.

These other attributes are automatically generated and maintained, so you'll
probably never have a reason to change them:

co_consts
    A list of constants used by the code; the first (zeroth?) constant is
    always ``None``.  Normally, this is automatically maintained; the
    ``.LOAD_CONST(value)`` method checks to see if the constant is already
    present in this list, and adds it if it is not there.

co_names
    A list of non-optimized or global variable names.  It's automatically
    updated whenever you invoke a method to generate an opcode that uses
    such names.

co_code
    A byte array containing the generated code.  Don't mess with this.

co_firstlineno
    The first line number of the generated code.  It automatically gets set
    if you call ``.set_lineno()`` before generating any code; otherwise it
    defaults to zero.

co_lnotab
    A byte array containing a generated line number table.  It's automatically
    generated, so don't mess with it.

co_stacksize
    The maximum amount of stack space the code will require to run.  This
    value is updated automatically as you generate code or change
    the ``stack_size`` attribute.



Stack Size Tracking and Dead Code Detection
===========================================

``Code`` objects automatically track the predicted stack size as code is
generated, by updating the ``stack_size`` attribute as each operation occurs.
A history is kept so that backward jumps can be checked to ensure that the
current stack height is the same as at the jump's target.  Similarly, when
forward jumps are resolved, the stack size at the jump target is checked
against the stack size at the jump's origin.  If there are multiple jumps to
the same location, they must all have the same stack size at the origin and
the destination.

In addition, whenever any unconditional jump code is generated (i.e.
``JUMP_FORWARD``, ``BREAK_LOOP``, ``CONTINUE_LOOP``, ``JUMP_ABSOLUTE``, or
``RETURN_VALUE``), the predicted ``stack_size`` is set to ``None``.  This
means that the ``Code`` object does not know what the stack size will be at
the current location.  You cannot issue *any* instructions when the predicted
stack size is ``None``, as you will receive an ``AssertionError``::

    >>> c = Code()
    >>> fwd = c.JUMP_FORWARD()
    >>> print c.stack_size  # forward jump marks stack size as unknown
    None

    >>> c.LOAD_CONST(42)
    Traceback (most recent call last):
      ...
    AssertionError: Unknown stack size at this location

Instead, you must resolve a forward reference (or define a previously-jumped to
label).  This will propagate the stack size at the source of the jump to the
current location, updating the stack size::

    >>> fwd()
    >>> c.stack_size
    0

Note, by the way, that this means it is impossible for you to generate static
"dead code".  In other words, you cannot generate code that isn't reachable.
You should therefore check if ``stack_size`` is ``None`` before generating
code that might be unreachable.  For example, consider this ``If``
implementation::

    >>> def If(cond, then, else_=Pass, code=None):
    ...     if code is None:
    ...         return cond, then, else_
    ...     else_clause = Label()
    ...     end_if = Label()
    ...     code(cond, else_clause.JUMP_IF_FALSE_OR_POP, then)
    ...     code(end_if.JUMP_FORWARD, else_clause, Code.POP_TOP, else_)
    ...     code(end_if)
    >>> If = nodetype()(If)

It works okay if there's no dead code::

    >>> c = Code()
    >>> c( If(Local('a'), 42, 55) )
    >>> dump(c.code())
                    LOAD_FAST                0 (a)
                    JUMP_IF_FALSE           L1
                    POP_TOP
                    LOAD_CONST               1 (42)
                    JUMP_FORWARD            L2
            L1:     POP_TOP
                    LOAD_CONST               2 (55)

But it breaks if you end the "then" block with a return::

    >>> c = Code()
    >>> c( If(23, Return(42), 55) )
    Traceback (most recent call last):
      ...
    AssertionError: Unknown stack size at this location

What we need is something like this instead::

    >>> def If(cond, then, else_=Pass, code=None):
    ...     if code is None:
    ...         return cond, then, else_
    ...     else_clause = Label()
    ...     end_if = Label()
    ...     code(cond, else_clause.JUMP_IF_FALSE_OR_POP, then)
    ...     if code.stack_size is not None:
    ...         end_if.JUMP_FORWARD(code)
    ...     code(else_clause, Code.POP_TOP, else_, end_if)           
    >>> If = nodetype()(If)

As you can see, the dead code is now eliminated::

    >>> c = Code()
    >>> c( If(Local('a'), Return(42), 55) )
    >>> dump(c.code())
                    LOAD_FAST                0 (a)
                    JUMP_IF_FALSE           L1
                    POP_TOP
                    LOAD_CONST               1 (42)
                    RETURN_VALUE
            L1:     POP_TOP
                    LOAD_CONST               2 (55)


Blocks, Loops, and Exception Handling
=====================================

The Python ``SETUP_FINALLY``, ``SETUP_EXCEPT``, and ``SETUP_LOOP`` opcodes
all create "blocks" that go on the frame's "block stack" at runtime.  Each of
these opcodes *must* be matched with *exactly one* ``POP_BLOCK`` opcode -- no
more, and no less.  ``Code`` objects enforce this using an internal block stack
that matches each setup with its corresponding ``POP_BLOCK``.  Trying to pop
a nonexistent block, or trying to generate code when unclosed blocks exist is
an error::

    >>> c = Code()
    >>> c.POP_BLOCK()
    Traceback (most recent call last):
      ...
    AssertionError: Not currently in a block

    >>> c.SETUP_FINALLY()
    >>> c.code()
    Traceback (most recent call last):
      ...
    AssertionError: 1 unclosed block(s)

    >>> c.POP_BLOCK()
    >>> c.code()
    <code object <lambda> ...>


Exception Stack Size Adjustment
-------------------------------

When you issue a ``SETUP_EXCEPT`` or ``SETUP_FINALLY``, the code's maximum
stack size is raised to ensure that it's at least 3 items higher than
the current stack size.  That way, there will be room for the items that Python
puts on the stack when jumping to a block's exception handling code::

    >>> c = Code()
    >>> c.SETUP_FINALLY()
    >>> c.stack_size, c.co_stacksize
    (0, 3)

As you can see, the current stack size is unchanged, but the maximum stack size
has increased.  This increase is relative to the current stack size, though;
it's not an absolute increase::

    >>> c = Code()
    >>> c(1,2,3,4, *[Code.POP_TOP]*4)   # push 4 things, then pop 'em
    >>> c.SETUP_FINALLY()
    >>> c.stack_size, c.co_stacksize
    (0, 4)

And this stack adjustment doesn't happen for loops, because they don't have
exception handlers::

    >>> c = Code()
    >>> c.SETUP_LOOP()
    >>> c.stack_size, c.co_stacksize
    (0, 0)


Try/Except Blocks
-----------------

In the case of ``SETUP_EXCEPT``, the *current* stack size is increased by 3
after a ``POP_BLOCK``, because the code that follows will be an exception
handler and will thus always have exception items on the stack::

    >>> c = Code()
    >>> c.SETUP_EXCEPT()
    >>> else_ = c.POP_BLOCK()
    >>> c.stack_size, c.co_stacksize
    (3, 3)

When a ``POP_BLOCK()`` is matched with a ``SETUP_EXCEPT``, it automatically
emits a ``JUMP_FORWARD`` and returns a forward reference that should be called
back when the "else" clause or end of the entire try/except statement is
reached::

    >>> c.POP_TOP()     # get rid of exception info
    >>> c.POP_TOP()
    >>> c.POP_TOP()
    >>> else_()
    >>> c.return_()
    >>> dump(c.code())
                    SETUP_EXCEPT            L1
                    POP_BLOCK
                    JUMP_FORWARD            L2
            L1:     POP_TOP
                    POP_TOP
                    POP_TOP
            L2:     LOAD_CONST               0 (None)
                    RETURN_VALUE

In the example above, an empty block executes with an exception handler that
begins at offset 7.  When the block is done, it jumps forward to the end of
the try/except construct at offset 10.  The exception handler does nothing but
remove the exception information from the stack before it falls through to the
end.

Note, by the way, that it's usually easier to use labels to define blocks
like this::

    >>> c = Code()
    >>> done = Label()
    >>> c(
    ...     done.SETUP_EXCEPT,
    ...     done.POP_BLOCK,
    ...         Code.POP_TOP, Code.POP_TOP, Code.POP_TOP,
    ...     done,
    ...     Return()
    ... )

    >>> dump(c.code())
                    SETUP_EXCEPT             L1
                    POP_BLOCK
                    JUMP_FORWARD             L2
            L1:     POP_TOP
                    POP_TOP
                    POP_TOP
            L2:     LOAD_CONST               0 (None)
                    RETURN_VALUE

(Labels have a ``POP_BLOCK`` attribute that you can pass in when generating
code.)

And, for generating typical try/except blocks, you can use the ``TryExcept``
node type, which takes a body, a sequence of exception-type/handler pairs,
and an optional "else" clause::

    >>> from peak.util.assembler import TryExcept
    >>> c = Code()
    >>> c.return_(
    ...     TryExcept(
    ...         Return(1),                                      # body
    ...         [(Const(KeyError),2), (Const(TypeError),3)],    # handlers
    ...         Return(4)                                       # else clause
    ...     )
    ... )

    >>> dump(c.code())
                    SETUP_EXCEPT            L1
                    LOAD_CONST               1 (1)
                    RETURN_VALUE
                    POP_BLOCK
                    JUMP_FORWARD            L4
            L1:     DUP_TOP
                    LOAD_CONST               2 (<...exceptions.KeyError...>)
                    COMPARE_OP              10 (exception match)
                    JUMP_IF_FALSE           L2
                    POP_TOP
                    POP_TOP
                    POP_TOP
                    POP_TOP
                    LOAD_CONST               3 (2)
                    JUMP_FORWARD            L5
            L2:     POP_TOP
                    DUP_TOP
                    LOAD_CONST               4 (<...exceptions.TypeError...>)
                    COMPARE_OP              10 (exception match)
                    JUMP_IF_FALSE           L3
                    POP_TOP
                    POP_TOP
                    POP_TOP
                    POP_TOP
                    LOAD_CONST               5 (3)
                    JUMP_FORWARD            L5
            L3:     POP_TOP
                    END_FINALLY
            L4:     LOAD_CONST               6 (4)
                    RETURN_VALUE
            L5:     RETURN_VALUE


Try/Finally Blocks
------------------

When a ``POP_BLOCK()`` is matched with a ``SETUP_FINALLY``, it automatically
emits a ``LOAD_CONST(None)``, so that when the corresponding ``END_FINALLY``
is reached, it will know that the "try" block exited normally.  Thus, the
normal pattern for producing a try/finally construct is as follows::

    >>> c = Code()
    >>> c.SETUP_FINALLY()
    >>> # "try" suite goes here
    >>> c.POP_BLOCK()
    >>> # "finally" suite goes here
    >>> c.END_FINALLY()

And it produces code that looks like this::

    >>> dump(c.code())
                    SETUP_FINALLY           L1
                    POP_BLOCK
                    LOAD_CONST               0 (None)
            L1:     END_FINALLY

The ``END_FINALLY`` opcode will remove 1, 2, or 3 values from the stack at
runtime, depending on how the "try" block was exited.  In the case of simply
"falling off the end" of the "try" block, however, the inserted
``LOAD_CONST(None)`` puts one value on the stack, and that one value is popped
off by the ``END_FINALLY``.  For that reason, ``Code`` objects treat
``END_FINALLY`` as if it always popped exactly one value from the stack, even
though at runtime this may vary.  This means that the estimated stack levels
within the "finally" clause may not be accurate -- which is why ``POP_BLOCK()``
adjusts the maximum expected stack size to accomodate up to three values being
put on the stack by the Python interpreter for exception handling.

For your convenience, the ``TryFinally`` node type can also be used to generate
try/finally blocks::

    >>> from peak.util.assembler import TryFinally
    >>> c = Code()
    >>> c( TryFinally(ExprStmt(1), ExprStmt(2)) )
    >>> dump(c.code())
                    SETUP_FINALLY           L1
                    LOAD_CONST               1 (1)
                    POP_TOP
                    POP_BLOCK
                    LOAD_CONST               0 (None)
            L1:     LOAD_CONST               2 (2)
                    POP_TOP
                    END_FINALLY


Loops
-----

The ``POP_BLOCK`` for a loop marks the end of the loop body, and the beginning
of the "else" clause, if there is one.  It returns a forward reference that
should be called back either at the end of the "else" clause, or immediately if
there is no "else".  Any ``BREAK_LOOP`` opcodes that appear in the loop body
will jump ahead to the point at which the forward reference is resolved.

Here, we'll generate a loop that counts down from 5 to 0, with an "else" clause
that returns 42.  Three labels are needed: one to mark the end of the overall
block, one that's looped back to, and one that marks the "else" clause::

    >>> c = Code()
    >>> block = Label()
    >>> loop = Label()
    >>> else_ = Label()
    >>> c(
    ...     block.SETUP_LOOP,
    ...         5,      # initial setup - this could be a GET_ITER instead
    ...     loop,
    ...         else_.JUMP_IF_FALSE,        # while x:
    ...         1, Code.BINARY_SUBTRACT,    #     x -= 1
    ...         loop.CONTINUE_LOOP,
    ...     else_,                          # else:
    ...         Code.POP_TOP,
    ...     block.POP_BLOCK,
    ...         Return(42),                 #     return 42
    ...     block,
    ...     Return()
    ... )

    >>> dump(c.code())
                    SETUP_LOOP              L3
                    LOAD_CONST               1 (5)
            L1:     JUMP_IF_FALSE           L2
                    LOAD_CONST               2 (1)
                    BINARY_SUBTRACT
                    JUMP_ABSOLUTE           L1
            L2:     POP_TOP
                    POP_BLOCK
                    LOAD_CONST               3 (42)
                    RETURN_VALUE
            L3:     LOAD_CONST               0 (None)
                    RETURN_VALUE

    >>> eval(c.code())
    42


Break and Continue
------------------

The ``BREAK_LOOP`` and ``CONTINUE_LOOP`` opcodes can only be used inside of
an active loop::

    >>> c = Code()
    >>> c.BREAK_LOOP()
    Traceback (most recent call last):
      ...
    AssertionError: Not inside a loop

    >>> c.CONTINUE_LOOP(c.here())
    Traceback (most recent call last):
      ...
    AssertionError: Not inside a loop

And ``CONTINUE_LOOP`` is automatically replaced with a ``JUMP_ABSOLUTE`` if
it occurs directly inside a loop block::

    >>> c.LOAD_CONST(57)
    >>> c.SETUP_LOOP()
    >>> fwd = c.JUMP_IF_TRUE()
    >>> c.CONTINUE_LOOP(c.here())
    >>> fwd()
    >>> c.BREAK_LOOP()
    >>> c.POP_BLOCK()()
    >>> dump(c.code())
                    LOAD_CONST               1 (57)
                    SETUP_LOOP              L3
                    JUMP_IF_TRUE            L2
            L1:     JUMP_ABSOLUTE           L1
            L2:     BREAK_LOOP
                    POP_BLOCK

In other words, ``CONTINUE_LOOP`` only really emits a ``CONTINUE_LOOP`` opcode
if it's inside some other kind of block within the loop, e.g. a "try" clause::

    >>> c = Code()
    >>> c.LOAD_CONST(57)
    >>> c.SETUP_LOOP()
    >>> loop = c.here()
    >>> c.SETUP_FINALLY()
    >>> fwd = c.JUMP_IF_TRUE()
    >>> c.CONTINUE_LOOP(loop)
    >>> fwd()
    >>> c.POP_BLOCK()
    >>> c.END_FINALLY()
    >>> c.POP_BLOCK()()
    >>> dump(c.code())
                    LOAD_CONST               1 (57)
                    SETUP_LOOP              L4
            L1:     SETUP_FINALLY           L3
                    JUMP_IF_TRUE            L2
                    CONTINUE_LOOP           L1
            L2:     POP_BLOCK
                    LOAD_CONST               0 (None)
            L3:     END_FINALLY
                    POP_BLOCK

``for`` Loops
-------------

There is a ``For()`` node type available for generating simple loops (without
break/continue support).  It takes an iterable expression, an assignment
clause, and a loop body::

    >>> from peak.util.assembler import For
    >>> y = Call(Const(range), (3,))
    >>> x = LocalAssign('x')
    >>> body = Suite([Local('x'), Code.PRINT_EXPR])

    >>> c = Code()
    >>> c(For(y, x, body))  # for x in range(3): print x
    >>> c.return_()
    >>> dump(c.code())
                    LOAD_CONST               1 ([0, 1, 2])
                    GET_ITER
            L1:     FOR_ITER                L2
                    STORE_FAST               0 (x)
                    LOAD_FAST                0 (x)
                    PRINT_EXPR
                    JUMP_ABSOLUTE           L1
            L2:     LOAD_CONST               0 (None)
                    RETURN_VALUE

The arguments are given in execution order: first the "in" value of the loop,
then the assignment to a loop variable, and finally the body of the loop.  The
distinction between the assignment and body, however, is only for clarity and
convenience (to avoid needing to glue the assignment to the body with a
``Suite``).  If you already have a suite or only need one node for the entire
loop body, you can do the same thing with only two arguments::

    >>> c = Code()
    >>> c(For(y, Code.PRINT_EXPR))
    >>> c.return_()
    >>> dump(c.code())
                    LOAD_CONST               1 ([0, 1, 2])
                    GET_ITER
            L1:     FOR_ITER                L2
                    PRINT_EXPR
                    JUMP_ABSOLUTE           L1
            L2:     LOAD_CONST               0 (None)
                    RETURN_VALUE

Notice, by the way, that ``For()`` does NOT set up a loop block for you, so if
you want to be able to use break and continue, you'll need to wrap the loop in
a labelled SETUP_LOOP/POP_BLOCK pair, as described in the preceding sections.


List Comprehensions
-------------------

In order to generate correct list comprehension code for the target Python
version, you must use the ``ListComp()`` and ``LCAppend()`` node types.  This
is because Python versions 2.4 and up store the list being built in a temporary
variable, and use a special ``LIST_APPEND`` opcode to append values, while 2.3
stores the list's ``append()`` method in the temporary variable, and calls it
to append values.

The ``ListComp()`` node wraps a code body (usually a ``For()`` loop) and
manages the creation and destruction of a temporary variable (e.g. ``_[1]``,
``_[2]``, etc.).  The ``LCAppend()`` node type wraps a value or expression to
be appended to the innermost active ``ListComp()`` in progress::

    >>> from peak.util.assembler import ListComp, LCAppend
    >>> c = Code()
    >>> simple = ListComp(For(y, x, LCAppend(Local('x'))))
    >>> c.return_(simple)
    >>> eval(c.code())
    [0, 1, 2]

    >>> c = Code()
    >>> c.return_(ListComp(For(y, x, LCAppend(simple))))
    >>> eval(c.code())
    [[0, 1, 2], [0, 1, 2], [0, 1, 2]]


Closures and Nested Functions
=============================

Free and Cell Variables
-----------------------

To implement closures and nested scopes, your code objects must use "free" or
"cell" variables in place of regular "fast locals".  A "free" variable is one
that is defined in an outer scope, and a "cell" variable is one that's defined
in the current scope, but will also be used by nested functions.

The simplest way to set up free or cell variables is to use a code object's
``makefree(names)`` and ``makecells(names)`` methods::

    >>> c = Code()
    >>> c.co_cellvars
    ()
    >>> c.co_freevars
    ()

    >>> c.makefree(['x', 'y'])
    >>> c.makecells(['z'])

    >>> c.co_cellvars
    ('z',)
    >>> c.co_freevars
    ('x', 'y')

When a name has been defined as a free or cell variable, the ``_DEREF`` opcode
variants are used to generate ``Local()`` and ``LocalAssign()`` nodes::

    >>> c((Local('x'), Local('y')), LocalAssign('z'))
    >>> dis(c.code())
      0           0 LOAD_DEREF               1 (x)
                  3 LOAD_DEREF               2 (y)
                  6 BUILD_TUPLE              2
                  9 STORE_DEREF              0 (z)

If you have already written code in a code object that operates on the relevant
locals, the code is retroactively patched to use the ``_DEREF`` opcodes::

    >>> c = Code()
    >>> c((Local('x'), Local('y')), LocalAssign('z'))
    >>> dis(c.code())
      0           0 LOAD_FAST                0 (x)
                  3 LOAD_FAST                1 (y)
                  6 BUILD_TUPLE              2
                  9 STORE_FAST               2 (z)

    >>> c.makefree(['x', 'y'])
    >>> c.makecells(['z'])

    >>> dis(c.code())
      0           0 LOAD_DEREF               1 (x)
                  3 LOAD_DEREF               2 (y)
                  6 BUILD_TUPLE              2
                  9 STORE_DEREF              0 (z)

This means that you can defer the decision of which locals are free/cell
variables until the code is ready to be generated.  In fact, by passing in
a "parent" code object to the ``.code()`` method, you can get BytecodeAssembler
to automatically call ``makefree()`` and ``makecells()`` for the correct
variable names in the child and parent code objects, as we'll see in the next
section.


Nested Code Objects
-------------------

To create a code object for use in a nested scope, you can use the parent code
object's ``nested()`` method.  It works just like the ``from_spec()``
classmethod, except that the ``co_filename`` of the parent is copied to the
child::

    >>> p = Code()
    >>> p.co_filename = 'testname'

    >>> c = p.nested('sub', ['a','b'], 'c', 'd')

    >>> c.co_name
    'sub'
    
    >>> c.co_filename
    'testname'

    >>> tuple(inspect.getargs(c.code(p)))
    (['a', 'b'], 'c', 'd')

Notice that you must pass the parent code object to the child's ``.code()``
method to ensure that free/cell variables are properly set up.  When the
``code()`` method is given another code object as a parameter, it automatically
converts any locally-read (but not written) to "free" variables in the child
code, and ensures that those same variables become "cell" variables in the
supplied parent code object::

    >>> p.LOAD_CONST(42)
    >>> p(LocalAssign('a'))
    >>> dis(p.code())
      0           0 LOAD_CONST               1 (42)
                  3 STORE_FAST               0 (a)
    
    >>> c = p.nested()
    >>> c(Local('a'))

    >>> dis(c.code(p))
      0           0 LOAD_DEREF               0 (a)

    >>> dis(p.code())
      0           0 LOAD_CONST               1 (42)
                  3 STORE_DEREF              0 (a)

Notice that the ``STORE_FAST`` in the parent code object was automatically
patched to a ``STORE_DEREF``, with an updated offset if applicable.  Any
future use of ``Local('a')`` or ``LocalAssign('a')`` in the parent or child
code objects will now refer to the free/cell variable, rather than the "local"
variable::

    >>> p(Local('a'))
    >>> dis(p.code())
      0           0 LOAD_CONST               1 (42)
                  3 STORE_DEREF              0 (a)
                  6 LOAD_DEREF               0 (a)

    >>> c(LocalAssign('a'))
    >>> dis(c.code(p))
      0           0 LOAD_DEREF               0 (a)
                  3 STORE_DEREF              0 (a)


``Function()``
--------------

The ``Function(body, name='<lambda>', args=(), var=None, kw=None, defaults=())``
node type creates a function object from the specified body and the optional
name, argument specs, and defaults.  The ``Function()`` node generates code to
create the function object with the appropriate defaults and closure (if
applicable), and any needed free/cell variables are automatically set up in the
parent and child code objects.  The newly generated function will be on top of
the stack at the end of the generated code::

    >>> from peak.util.assembler import Function
    >>> c = Code()
    >>> c.co_filename = '<string>'
    >>> c.return_(Function(Return(Local('a')), 'f', ['a'], defaults=[42]))
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (42)
                  3 LOAD_CONST               2 (<... f ..., file "<string>", line -1>)
                  6 MAKE_FUNCTION            1
                  9 RETURN_VALUE

Now that we've generated the code for a function returning a function, let's
run it, to get the function we defined::

    >>> f = eval(c.code())
    >>> f
    <function f at ...>

    >>> tuple(inspect.getargspec(f))
    (['a'], None, None, (42,))

    >>> f()
    42

    >>> f(99)
    99

Now let's create a doubly nested function, with some extras::

    >>> c = Code()
    >>> c.co_filename = '<string>'
    >>> c.return_(
    ...     Function(Return(Function(Return(Local('a')))),
    ...     'f', ['a', 'b'], 'c', 'd', [99, 66])
    ... )
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (99)
                  3 LOAD_CONST               2 (66)
                  6 LOAD_CONST               3 (<... f ..., file "<string>", line -1>)
                  9 MAKE_FUNCTION            2
                 12 RETURN_VALUE

    >>> f = eval(c.code())
    >>> f
    <function f at ...>

    >>> tuple(inspect.getargspec(f))
    (['a', 'b'], 'c', 'd', (99, 66))

    >>> dis(f)
      0           0 LOAD_CLOSURE             0 (a)
                  ... LOAD_CONST               1 (<... <lambda> ..., file "<string>", line -1>)
                  ... MAKE_CLOSURE             0
                  ... RETURN_VALUE

    >>> dis(f())
      0           0 LOAD_DEREF               0 (a)
                  3 RETURN_VALUE    

    >>> f(42)()
    42

    >>> f()()
    99

As you can see, ``Function()`` not only takes care of setting up free/cell
variables in all the relevant scopes, it also chooses whether to use
``MAKE_FUNCTION`` or ``MAKE_CLOSURE``, and generates code for the defaults.

(Note, by the way, that the `defaults` argument should be a sequence of
generatable expressions; in the examples here, we used numbers, but they could
have been arbitrary expression nodes.)


----------------------
Internals and Doctests
----------------------

Line number tracking::

    >>> def simple_code(flno, slno, consts=1, ):
    ...     c = Code()
    ...     c.set_lineno(flno)
    ...     for i in range(consts): c.LOAD_CONST(None)
    ...     c.set_lineno(slno)
    ...     c.RETURN_VALUE()
    ...     return c.code()

    >>> dis(simple_code(1,1))
      1           0 LOAD_CONST               0 (None)
                  3 RETURN_VALUE

    >>> simple_code(1,1).co_stacksize
    1

    >>> dis(simple_code(13,414))
     13           0 LOAD_CONST               0 (None)
    414           3 RETURN_VALUE

    >>> dis(simple_code(13,14,100))
     13           0 LOAD_CONST               0 (None)
                  3 LOAD_CONST               0 (None)
    ...
     14         300 RETURN_VALUE

    >>> simple_code(13,14,100).co_stacksize
    100

    >>> dis(simple_code(13,572,120))
     13           0 LOAD_CONST               0 (None)
                  3 LOAD_CONST               0 (None)
    ...
    572         360 RETURN_VALUE


Stack size tracking::

    >>> c = Code()          # 0
    >>> c.LOAD_CONST(1)     # 1
    >>> c.POP_TOP()         # 0
    >>> c.LOAD_CONST(2)     # 1
    >>> c.LOAD_CONST(3)     # 2
    >>> c.co_stacksize
    2
    >>> c.stack_history
    [0, ..., 1, 0, ..., 1]
    >>> c.BINARY_ADD()      # 1
    >>> c.LOAD_CONST(4)     # 2
    >>> c.co_stacksize
    2
    >>> c.stack_history
    [0, ..., 1, 0, 1, ..., 2, ..., 1]
    >>> c.LOAD_CONST(5)
    >>> c.LOAD_CONST(6)
    >>> c.co_stacksize
    4
    >>> c.POP_TOP()
    >>> c.stack_size
    3

Stack underflow detection/recovery, and global/local variable names::

    >>> c = Code()
    >>> c.LOAD_GLOBAL('foo')
    >>> c.stack_size
    1
    >>> c.STORE_ATTR('bar')     # drops stack by 2
    Traceback (most recent call last):
      ...
    AssertionError: Stack underflow

    >>> c.co_names  # 'bar' isn't added unless success
    ['foo']

    >>> c.LOAD_ATTR('bar')
    >>> c.co_names
    ['foo', 'bar']

    >>> c.DELETE_FAST('baz')
    >>> c.co_varnames
    ['baz']

    >>> dis(c.code())
      0           0 LOAD_GLOBAL              0 (foo)
                  3 LOAD_ATTR                1 (bar)
                  6 DELETE_FAST              0 (baz)

Code iteration::

    >>> c.DUP_TOP()
    >>> c.return_(Code.POP_TOP)
    >>> list(c) == [
    ...     (0, op.LOAD_GLOBAL, 0),
    ...     (3, op.LOAD_ATTR, 1),
    ...     (6, op.DELETE_FAST, 0),
    ...     (9, op.DUP_TOP, None),
    ...     (10, op.POP_TOP, None),
    ...     (11, op.RETURN_VALUE, None)
    ... ]
    True

Code patching::

    >>> c = Code()
    >>> c.LOAD_CONST(42)
    >>> c.STORE_FAST('x')
    >>> c.LOAD_FAST('x')
    >>> c.DELETE_FAST('x')
    >>> c.RETURN_VALUE()

    >>> dis(c.code())
      0           0 LOAD_CONST               1 (42)
                  3 STORE_FAST               0 (x)
                  6 LOAD_FAST                0 (x)
                  9 DELETE_FAST              0 (x)
                 12 RETURN_VALUE


    >>> c.co_varnames
    ['x']
    >>> c.co_varnames.append('y')

    >>> c._patch(
    ...     {op.LOAD_FAST:  op.LOAD_FAST,
    ...      op.STORE_FAST: op.STORE_FAST,
    ...      op.DELETE_FAST: op.DELETE_FAST},
    ...     {0: 1}
    ... )

    >>> dis(c.code())
      0           0 LOAD_CONST               1 (42)
                  3 STORE_FAST               1 (y)
                  6 LOAD_FAST                1 (y)
                  9 DELETE_FAST              1 (y)
                 12 RETURN_VALUE

    >>> c._patch({op.RETURN_VALUE: op.POP_TOP})
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (42)
                  3 STORE_FAST               1 (y)
                  6 LOAD_FAST                1 (y)
                  9 DELETE_FAST              1 (y)
                 12 POP_TOP

Converting locals to free/cell vars::

    >>> c = Code()
    >>> c.LOAD_CONST(42)
    >>> c.STORE_FAST('x')
    >>> c.LOAD_FAST('x')

    >>> dis(c.code())
      0           0 LOAD_CONST               1 (42)
                  3 STORE_FAST               0 (x)
                  6 LOAD_FAST                0 (x)

    >>> c.co_freevars = 'y', 'x'
    >>> c.co_cellvars = 'z',

    >>> c._locals_to_cells()
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (42)
                  3 STORE_DEREF              2 (x)
                  6 LOAD_DEREF               2 (x)

    >>> c.DELETE_FAST('x')
    >>> c._locals_to_cells()
    Traceback (most recent call last):
      ...
    AssertionError: Can't delete local 'x' used in nested scope

    >>> c = Code()
    >>> c.LOAD_CONST(42)
    >>> c.STORE_FAST('x')
    >>> c.LOAD_FAST('x')

    >>> c.co_freevars
    ()
    >>> c.makefree(['x'])
    >>> c.co_freevars
    ('x',)

    >>> dis(c.code())
      0           0 LOAD_CONST               1 (42)
                  3 STORE_DEREF              0 (x)
                  6 LOAD_DEREF               0 (x)

    >>> c = Code()
    >>> c.LOAD_CONST(42)
    >>> c.STORE_FAST('x')
    >>> c.LOAD_FAST('x')
    >>> c.makecells(['x'])
    >>> c.co_freevars
    ()
    >>> c.co_cellvars
    ('x',)
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (42)
                  3 STORE_DEREF              0 (x)
                  6 LOAD_DEREF               0 (x)
    
    >>> c = Code()
    >>> c.LOAD_CONST(42)
    >>> c.STORE_FAST('x')
    >>> c.LOAD_FAST('x')
    >>> c.makefree('x')
    >>> c.makecells(['y'])
    >>> c.co_freevars
    ('x',)
    >>> c.co_cellvars
    ('y',)
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (42)
                  3 STORE_DEREF              1 (x)
                  6 LOAD_DEREF               1 (x)

    >>> c = Code()
    >>> c.co_flags &= ~op.CO_OPTIMIZED
    >>> c.makecells(['q'])
    Traceback (most recent call last):
      ...
    AssertionError: Can't use cellvars in unoptimized scope
    


Auto-free promotion with code parent:

    >>> p = Code()
    >>> c = Code()
    >>> c.LOAD_FAST('x')
    >>> dis(c.code(p))
      0           0 LOAD_DEREF               0 (x)
    >>> p.co_cellvars
    ('x',)

    >>> p = Code()
    >>> c = Code.from_function(lambda x,y,z=2: None)
    >>> c.LOAD_FAST('x')
    >>> c.LOAD_FAST('y')
    >>> c.LOAD_FAST('z')
    
    >>> dis(c.code(p))
      0           0 LOAD_FAST                0 (x)
                  3 LOAD_FAST                1 (y)
                  6 LOAD_FAST                2 (z)
    >>> p.co_cellvars
    ()

    >>> c.LOAD_FAST('q')
    >>> dis(c.code(p))
      0           0 LOAD_FAST                0 (x)
                  3 LOAD_FAST                1 (y)
                  6 LOAD_FAST                2 (z)
                  9 LOAD_DEREF               0 (q)
    >>> p.co_cellvars
    ('q',)

    >>> p = Code()
    >>> c = Code.from_function(lambda x,*y,**z: None)
    >>> c.LOAD_FAST('q')
    >>> c.LOAD_FAST('x')
    >>> c.LOAD_FAST('y')
    >>> c.LOAD_FAST('z')
    >>> dis(c.code(p))
      0           0 LOAD_DEREF               0 (q)
                  3 LOAD_FAST                0 (x)
                  6 LOAD_FAST                1 (y)
                  9 LOAD_FAST                2 (z)
    >>> p.co_cellvars
    ('q',)

    >>> p = Code()
    >>> c = Code.from_function(lambda x,*y: None)
    >>> c.LOAD_FAST('x')
    >>> c.LOAD_FAST('y')
    >>> c.LOAD_FAST('z')
    >>> dis(c.code(p))
      0           0 LOAD_FAST                0 (x)
                  3 LOAD_FAST                1 (y)
                  6 LOAD_DEREF               0 (z)
    >>> p.co_cellvars
    ('z',)

    >>> p = Code()
    >>> c = Code.from_function(lambda x,**y: None)
    >>> c.LOAD_FAST('x')
    >>> c.LOAD_FAST('y')
    >>> c.LOAD_FAST('z')
    >>> dis(c.code(p))
      0           0 LOAD_FAST                0 (x)
                  3 LOAD_FAST                1 (y)
                  6 LOAD_DEREF               0 (z)
    >>> p.co_cellvars
    ('z',)


Stack tracking on jumps::

    >>> c = Code()
    >>> else_ = Label()
    >>> end = Label()
    >>> c(99, else_.JUMP_IF_TRUE_OR_POP, end.JUMP_FORWARD)
    >>> c(else_, Code.POP_TOP, end)
    >>> dump(c.code())
                    LOAD_CONST               1 (99)
                    JUMP_IF_TRUE            L1
                    POP_TOP
                    JUMP_FORWARD            L2
            L1:     POP_TOP

    >>> c.stack_size
    0
    >>> if sys.version>='2.7':
    ...     print c.stack_history == [0, 1, 1, 1,    0, 0, 0, None, None, 1]
    ... else:
    ...     print c.stack_history == [0, 1, 1, 1, 1, 1, 1, 0, None, None, 1]
    True
    

    >>> c = Code()
    >>> fwd = c.JUMP_FORWARD()
    >>> c.LOAD_CONST(42)    # forward jump marks stack size unknown
    Traceback (most recent call last):
      ...
    AssertionError: Unknown stack size at this location

    >>> c.stack_size = 0
    >>> c.LOAD_CONST(42)
    >>> fwd()
    Traceback (most recent call last):
      ...
    AssertionError: Stack level mismatch: actual=1 expected=0

    >>> from peak.util.assembler import For
    >>> c = Code()
    >>> c(For((), Code.POP_TOP, Pass))
    >>> c.return_()
    >>> dump(c.code())
                    BUILD_TUPLE              0
                    GET_ITER
            L1:     FOR_ITER                L2
                    POP_TOP
                    JUMP_ABSOLUTE           L1
            L2:     LOAD_CONST               0 (None)
                    RETURN_VALUE

    >>> c.stack_history
    [0, 1, 1, 1, 1, 2, 2, 2, 1, None, None, 0, 1, 1, 1]


Yield value::

    >>> import sys
    >>> from peak.util.assembler import CO_GENERATOR
    >>> c = Code()
    >>> c.co_flags & CO_GENERATOR
    0
    >>> c(42, Code.YIELD_VALUE)
    >>> c.stack_size == int(sys.version>='2.5')
    True
    >>> (c.co_flags & CO_GENERATOR) == CO_GENERATOR
    True

    
    
Sequence operators and stack tracking:



Function calls and raise::

    >>> c = Code()
    >>> c.LOAD_GLOBAL('locals')
    >>> c.CALL_FUNCTION()   # argc/kwargc default to 0
    >>> c.POP_TOP()
    >>> c.LOAD_GLOBAL('foo')
    >>> c.LOAD_CONST(1)
    >>> c.LOAD_CONST('x')
    >>> c.LOAD_CONST(2)
    >>> c.CALL_FUNCTION(1,1)    # argc, kwargc
    >>> c.POP_TOP()

    >>> dis(c.code())
      0           0 LOAD_GLOBAL              0 (locals)
                  3 CALL_FUNCTION            0
                  6 POP_TOP
                  7 LOAD_GLOBAL              1 (foo)
                 10 LOAD_CONST               1 (1)
                 13 LOAD_CONST               2 ('x')
                 16 LOAD_CONST               3 (2)
                 19 CALL_FUNCTION          257
                 22 POP_TOP

    >>> c = Code()
    >>> c.LOAD_GLOBAL('foo')
    >>> c.LOAD_CONST(1)
    >>> c.LOAD_CONST('x')
    >>> c.LOAD_CONST(2)
    >>> c.BUILD_MAP(0)
    >>> c.stack_size
    5
    >>> c.CALL_FUNCTION_KW(1,1)
    >>> c.POP_TOP()
    >>> c.stack_size
    0

    >>> c = Code()
    >>> c.LOAD_GLOBAL('foo')
    >>> c.LOAD_CONST(1)
    >>> c.LOAD_CONST('x')
    >>> c.LOAD_CONST(1)
    >>> c.BUILD_TUPLE(1)
    >>> c.CALL_FUNCTION_VAR(0,1)
    >>> c.POP_TOP()
    >>> c.stack_size
    0

    >>> c = Code()
    >>> c.LOAD_GLOBAL('foo')
    >>> c.LOAD_CONST(1)
    >>> c.LOAD_CONST('x')
    >>> c.LOAD_CONST(1)
    >>> c.BUILD_TUPLE(1)
    >>> c.BUILD_MAP(0)
    >>> c.CALL_FUNCTION_VAR_KW(0,1)
    >>> c.POP_TOP()
    >>> c.stack_size
    0

    >>> c = Code()
    >>> c.RAISE_VARARGS(0)
    >>> c.RAISE_VARARGS(1)
    Traceback (most recent call last):
      ...
    AssertionError: Stack underflow
    >>> c.LOAD_CONST(1)
    >>> c.RAISE_VARARGS(1)

    >>> dis(c.code())
      0           0 RAISE_VARARGS            0
                  3 LOAD_CONST               1 (1)
                  6 RAISE_VARARGS            1

Sequence building, unpacking, dup'ing::

    >>> c = Code()
    >>> c.LOAD_CONST(1)
    >>> c.LOAD_CONST(2)
    >>> c.BUILD_TUPLE(3)
    Traceback (most recent call last):
      ...
    AssertionError: Stack underflow

    >>> c.BUILD_LIST(3)
    Traceback (most recent call last):
      ...
    AssertionError: Stack underflow

    >>> c.BUILD_TUPLE(2)
    >>> c.stack_size
    1

    >>> c.UNPACK_SEQUENCE(2)
    >>> c.stack_size
    2
    >>> c.DUP_TOPX(3)
    Traceback (most recent call last):
      ...
    AssertionError: Stack underflow

    >>> c.DUP_TOPX(2)
    >>> c.stack_size
    4
    >>> c.LOAD_CONST(3)
    >>> c.BUILD_LIST(5)
    >>> c.stack_size
    1
    >>> c.UNPACK_SEQUENCE(5)
    >>> c.BUILD_SLICE(3)
    >>> c.stack_size
    3
    >>> c.BUILD_SLICE(3)
    >>> c.stack_size
    1
    >>> c.BUILD_SLICE(2)
    Traceback (most recent call last):
      ...
    AssertionError: Stack underflow

    >>> dis(c.code())
      0           0 LOAD_CONST               1 (1)
                  3 LOAD_CONST               2 (2)
                  6 BUILD_TUPLE              2
                  9 UNPACK_SEQUENCE          2
                 12 DUP_TOPX                 2
                 15 LOAD_CONST               3 (3)
                 18 BUILD_LIST               5
                 21 UNPACK_SEQUENCE          5
                 24 BUILD_SLICE              3
                 27 BUILD_SLICE              3

Stack levels for MAKE_FUNCTION/MAKE_CLOSURE::

    >>> c = Code()
    >>> c.MAKE_FUNCTION(0)
    Traceback (most recent call last):
      ...
    AssertionError: Stack underflow

    >>> c.LOAD_CONST(1)
    >>> c.LOAD_CONST(2) # simulate being a function
    >>> c.MAKE_FUNCTION(1)
    >>> c.stack_size
    1

    >>> c = Code()
    >>> c.MAKE_CLOSURE(0, 0)
    Traceback (most recent call last):
      ...
    AssertionError: Stack underflow

    >>> c = Code()
    >>> c.LOAD_CONST(1) # closure
    >>> if sys.version>='2.5': c.BUILD_TUPLE(1)
    >>> c.LOAD_CONST(2) # default
    >>> c.LOAD_CONST(3) # simulate being a function
    >>> c.MAKE_CLOSURE(1, 1)
    >>> c.stack_size
    1

    >>> c = Code()
    >>> c.LOAD_CONST(1)
    >>> c.LOAD_CONST(2)
    >>> if sys.version>='2.5': c.BUILD_TUPLE(2)
    >>> c.LOAD_CONST(3) # simulate being a function
    >>> c.MAKE_CLOSURE(0, 2)
    >>> c.stack_size
    1



Labels and backpatching forward references::

    >>> c = Code()
    >>> where = c.here()
    >>> c.LOAD_CONST(1)
    >>> c.JUMP_FORWARD(where)
    Traceback (most recent call last):
      ...
    AssertionError: Relative jumps can't go backwards


"Call" combinations::


    >>> c = Code()
    >>> c.set_lineno(1)
    >>> c(Call(Global('foo'), [Local('q')],
    ...        [('x',Const(1))], Local('starargs'))
    ... )
    >>> c.RETURN_VALUE()
    >>> dis(c.code())
      1           0 LOAD_GLOBAL              0 (foo)
                  3 LOAD_FAST                0 (q)
                  6 LOAD_CONST               1 ('x')
                  9 LOAD_CONST               2 (1)
                 12 LOAD_FAST                1 (starargs)
                 15 CALL_FUNCTION_VAR      257
                 18 RETURN_VALUE


    >>> c = Code()
    >>> c.set_lineno(1)
    >>> c(Call(Global('foo'), [Local('q')], [('x',Const(1))],
    ...        None, Local('kwargs'))
    ... )
    >>> c.RETURN_VALUE()
    >>> dis(c.code())
      1           0 LOAD_GLOBAL              0 (foo)
                  3 LOAD_FAST                0 (q)
                  6 LOAD_CONST               1 ('x')
                  9 LOAD_CONST               2 (1)
                 12 LOAD_FAST                1 (kwargs)
                 15 CALL_FUNCTION_KW       257
                 18 RETURN_VALUE


Cloning::

    >>> c = Code.from_function(lambda (x,y):1, True)
    >>> dis(c.code())
      1           0 LOAD_FAST                0 (.0)
                  3 UNPACK_SEQUENCE          2
                  6 STORE_FAST               1 (x)
                  9 STORE_FAST               2 (y)

    >>> c = Code.from_function(lambda x,(y,(z,a,b)):1, True)
    >>> dis(c.code())
      1           0 LOAD_FAST                1 (.1)
                  3 UNPACK_SEQUENCE          2
                  6 STORE_FAST               2 (y)
                  9 UNPACK_SEQUENCE          3
                 12 STORE_FAST               3 (z)
                 15 STORE_FAST               4 (a)
                 18 STORE_FAST               5 (b)

Constant folding for ``*args`` and ``**kw``::

    >>> c = Code()
    >>> c.return_(Call(Const(type), [], [], (1,)))
    >>> dis(c.code())
      0           0 LOAD_CONST               1 (<type 'int'>)
                  3 RETURN_VALUE


    >>> c = Code()
    >>> c.return_(Call(Const(dict), [], [], [], Const({'x':1})))
    >>> dis(c.code())
      0           0 LOAD_CONST               1 ({'x': 1})
                  3 RETURN_VALUE

Try/Except stack level tracking::

    >>> def class_or_type_of(expr):
    ...     return Suite([expr, TryExcept(
    ...         Suite([Getattr(Code.DUP_TOP, '__class__'), Code.ROT_TWO]),
    ...         [(Const(AttributeError), Call(Const(type), (Code.ROT_TWO,)))]
    ...     )])

    >>> def type_or_class(x): pass
    >>> c = Code.from_function(type_or_class)
    >>> c.return_(class_or_type_of(Local('x')))
    >>> dump(c.code())
                    LOAD_FAST                0 (x)
                    SETUP_EXCEPT            L1
                    DUP_TOP
                    LOAD_ATTR                0 (__class__)
                    ROT_TWO
                    POP_BLOCK
                    JUMP_FORWARD            L3
            L1:     DUP_TOP
                    LOAD_CONST               1 (<...exceptions.AttributeError...>)
                    COMPARE_OP              10 (exception match)
                    JUMP_IF_FALSE           L2
                    POP_TOP
                    POP_TOP
                    POP_TOP
                    POP_TOP
                    LOAD_CONST               2 (<type 'type'>)
                    ROT_TWO
                    CALL_FUNCTION            1
                    JUMP_FORWARD            L3
            L2:     POP_TOP
                    END_FINALLY
            L3:     RETURN_VALUE

    >>> type_or_class.func_code = c.code()
    >>> type_or_class(23)
    <type 'int'>
    




Demo: "Computed Goto"/"Switch Statement"
========================================

Finally, to give an example of a creative way to abuse Python bytecode, here
is an implementation of a simple "switch/case/else" structure::

    >>> from peak.util.assembler import LOAD_CONST, POP_BLOCK

    >>> import sys
    >>> WHY_CONTINUE = {'2.3':5}.get(sys.version[:3], 32)

    >>> def Switch(expr, cases, default=Pass, code=None):
    ...     if code is None:
    ...         return expr, tuple(cases), default
    ...
    ...     d = {}
    ...     else_block  = Label()
    ...     cleanup     = Label()
    ...     end_switch  = Label()
    ...
    ...     code(
    ...         end_switch.SETUP_LOOP,
    ...             Call(Const(d.get), [expr]),
    ...         else_block.JUMP_IF_FALSE,
    ...             WHY_CONTINUE, Code.END_FINALLY
    ...     )
    ...
    ...     cursize = code.stack_size - 1   # adjust for removed WHY_CONTINUE
    ...     for key, value in cases:
    ...         d[const_value(key)] = code.here()
    ...         code.stack_size = cursize
    ...         code(value)
    ...         if code.stack_size is not None: # if the code can fall through,
    ...             code(cleanup.JUMP_FORWARD)  # jump forward to the cleanup
    ...
    ...     code(
    ...         else_block,
    ...             Code.POP_TOP, default,
    ...         cleanup,
    ...             Code.POP_BLOCK,
    ...         end_switch
    ...     )
    >>> Switch = nodetype()(Switch)

    >>> c = Code()
    >>> c.co_argcount=1
    >>> c(Switch(Local('x'), [(1,Return(42)),(2,Return("foo"))], Return(27)))
    >>> c.return_()

    >>> f = new.function(c.code(), globals())
    >>> f(1)
    42
    >>> f(2)
    'foo'
    >>> f(3)
    27

    >>> dump(c.code())
                    SETUP_LOOP              L2
                    LOAD_CONST               1 (<...method get of dict...>)
                    LOAD_FAST                0 (x)
                    CALL_FUNCTION            1
                    JUMP_IF_FALSE           L1
                    LOAD_CONST               2 (...)
                    END_FINALLY
                    LOAD_CONST               3 (42)
                    RETURN_VALUE
                    LOAD_CONST               4 ('foo')
                    RETURN_VALUE
            L1:     POP_TOP
                    LOAD_CONST               5 (27)
                    RETURN_VALUE
                    POP_BLOCK
            L2:     LOAD_CONST               0 (None)
                    RETURN_VALUE


TODO
====

* Test NAME vs. FAST operators flag checks/sets

* Test code flags generation/cloning

* Exhaustive tests of all opcodes' stack history effects

* Test wide jumps and wide argument generation in general
