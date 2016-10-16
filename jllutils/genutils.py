from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __builtin__ import int

def typestr(var):
    """
    Returns the type of var as a simple string (rather than <type 'xxx'>)
    :param var: the variable to get the type of
    :return: the type of var as a string
    """
    s = "{0}".format(type(var))
    i = s.index("\'")
    s = s[i+1:]
    e = s.index("\'")
    s = s[:e]
    return s