from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __builtin__ import int

import cPickle
import numpy as np

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

def grab_pickle(pickle_file):
    """
    Wrapper function that loads a pickle file, ensuring that the necessary file object is closed properly.
    :param pickle_file: the path to the pickle file to load
    :return: the result of loading the file
    """
    with open(pickle_file, 'rb') as pobj:
        pkl_data = cPickle.load(pobj)
    return pkl_data

def isequaln(A, B):
    """
    True if two numpy arrays are equal, treating NaNs as equal and using the default tolerances for np.ma.allclose
    :param A: the first array to compare
    :param B: the second array to compare
    :return: True if the arrays are equal, false otherwise
    """
    if not isinstance(A, np.ndarray) or not isinstance(B, np.ndarray):
        raise TypeError('A and B must be numpy.ndarray instances')

    if A.shape != B.shape:
        return False

    A_masked = np.ma.masked_where(np.isnan(A), A)
    B_masked = np.ma.masked_where(np.isnan(B), B)
    return np.ma.allclose(A_masked, B_masked)

def chrange(start, stop, step=1):
    """
    An iterator for a range of characters
    :param start: the character for the beginning of the list
    :param stop: the character for the end of the list. Unlike a normal range(), this is inclusive
    :param step: the step between characters. Must be an integer
    :return: an iterator over characters.
    """

    start_int = ord(start)
    end_int = ord(stop)+1
    for i in range(start_int, end_int):
        yield chr(i)

def flatten(iterable):
    raise NotImplementedError('Still working on how to make this function work')
    flist = []
    try:
        for item in iterable:
            flist += flatten(item)
    except TypeError:
        # if iterable is not actually iterable
        return iterable
    else:
        return flist
