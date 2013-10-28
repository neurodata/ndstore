"""Standard TurboGears request hooks for CherryPy."""

__all__ = ['NestedVariablesHook']

from cherrypy import request
from formencode.variabledecode import NestedVariables


def NestedVariablesHook():
    """Request filter for handling nested variables.

    Turns request parameters with names in special dotted notation into
    nested dictionaries via the FormEncode NestedVariables validator.

    Stores the original parameters in the 'original_params' attribute.

    """
    try:
        params = request.params
    except AttributeError:
        pass
    else:
        request.original_params = params
        request.params = NestedVariables.to_python(params or {})

