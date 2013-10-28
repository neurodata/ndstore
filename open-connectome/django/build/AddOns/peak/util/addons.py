from peak.util.decorators import decorate, decorate_class, enclosing_frame, classy
from weakref import ref
import sys

__all__ = ['AddOn', 'ClassAddOn', 'Registry', 'addons_for']

_addons = {}

def addons_for(ob):
    """Get the dictionary that should contain add-ons for `ob`"""
    try:
        d = ob.__dict__
        sd = d.setdefault
        return d
    except (AttributeError, TypeError):
        r = ref(ob)
        try:
            return _addons[r]
        except KeyError:
            return _addons.setdefault(ref(ob, _addons.__delitem__), {})


def additional_tests():
    import doctest
    return doctest.DocFileSuite(
        'README.txt', package='__main__',
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE,
    )













class AddOn(classy):
    """Attach extra state to (almost) any object"""

    __slots__ = ()

    decorate(classmethod)
    def __class_call__(cls, ob, *data):
        a = addons_for(ob)
        addon_key = cls.addon_key(*data)
        try:
            return a[addon_key]
        except KeyError:
            # Use setdefault() to prevent race conditions
            ob = a.setdefault(addon_key, super(AddOn, cls).__class_call__(ob, *data))
            return ob

    decorate(classmethod)
    def addon_key(cls, *args):
        if args: return (cls,)+args
        return cls

    decorate(classmethod)
    def exists_for(cls, ob, *key):
        """Does an aspect of this type for the given key exist?"""
        return cls.addon_key(*key) in addons_for(ob)

    decorate(classmethod)
    def delete_from(cls, ob, *key):
        """Ensure an aspect of this type for the given key does not exist"""
        a = addons_for(ob)
        try:
            del a[cls.addon_key(*key)]
        except KeyError:
            pass

    def __init__(self, subject):
        pass




class ClassAddOn(AddOn):
    """Attachment/annotation for classes and types"""
    __slots__ = ()

    decorate(classmethod)
    def __class_call__(cls, ob, *data):
        addon_key = cls.addon_key(*data)
        d = ob.__dict__
        if addon_key in d:
            return d[addon_key]
        d2 = addons_for(ob)
        try:
            return d2[addon_key]
        except KeyError:
            # Use setdefault() to prevent race conditions
            ob = d2.setdefault(
                addon_key,
                super(ClassAddOn, cls).__class_call__(ob, *data)
            )
            return ob

    decorate(classmethod)
    def for_enclosing_class(cls, *args, **kw):
        if 'frame' in kw:
            frame = kw.pop('frame')
        else:
            if 'level' in kw:
                level = kw.pop('level')
            else:
                level = 2
            frame = sys._getframe(level)
        if kw:
            raise TypeError("Unexpected keyword arguments", kw)
        return cls.for_frame(frame, *args)







    decorate(classmethod)
    def for_frame(cls, frame, *args):
        a = enclosing_frame(frame).f_locals
        addon_key = cls.addon_key(*args)
        try:
            return a[addon_key]
        except KeyError:
            # Use setdefault() to prevent race conditions
            ob = a.setdefault(addon_key, type.__call__(cls, None, *args))
            # we use a lambda here so that if we are a registry, Python 2.5
            # won't consider our method equal to some other registry's method
            decorate_class(lambda c: ob.__decorate(c), frame=frame)
            return ob

    decorate(classmethod)
    def exists_for(cls, ob, *key):
        """Does an aspect of this type for the given key exist?"""
        addon_key = cls.addon_key(*key)
        return addon_key in ob.__dict__ or addon_key in addons_for(ob)

    decorate(classmethod)
    def delete_from(cls, ob, *key):
        """Class AddOns are not deletable!"""
        raise TypeError("ClassAddOns cannot be deleted")

    def __decorate(self, cls):
        self.created_for(cls)
        return cls

    def created_for(self, cls):
        """Override to access the decorated class, as soon as it's known"""

    def __init__(self, subject):
        """Ensure ``created_for()`` is called, if class already exists"""
        if subject is not None:
            self.created_for(subject)





class Registry(ClassAddOn, dict):
    """ClassAddOn that's a dictionary with mro-based inheritance"""

    __slots__ = ()

    def __new__(cls, subject):
        if cls is Registry:
            raise TypeError("You must subclass Registry to use it")
        return super(Registry, cls).__new__(cls)

    def __init__(self, subject):
        dict.__init__(self)
        super(Registry, self).__init__(subject)

    def created_for(self, cls):
        """Inherit the contents of base classes"""
        try:
            mro = cls.__mro__[::-1]
        except AttributeError:
            mro = type(cls.__name__, (cls,object), {}).__mro__[1:][::-1]

        data = {}
        self.defined_in_class = dict(self)

        mytype = type(self)
        for base in mro[:-1]:
            data.update(mytype(base))
        data.update(self)

        self.update(data)

    def set(self, key, value):
        if key in self and self[key]!=value:
            raise ValueError("%s[%r] already contains %r; can't set to %r"
                % (self.__class__.__name__, key, self[key], value)
            )
        self[key] = value




