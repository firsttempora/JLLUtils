from __future__ import print_function
import math

class _NumberName(object):
    def __init__(self):
        self.names = []
        self.values = []

    def add_name(self, name, value):
        self.names.append(name)
        self.values.append(value)

    def add_names(self, **kwargs):
        for k,v in kwargs.items():
            self.add_name(k, v)

    def value_name(self, value):
        i = self.values.index(value)
        return self.names[i]


_powers_of_10 = _NumberName()
_powers_of_10.add_names(thousand=3, million=6, billion=9, trillion=12, quadrillion=15, quintillion=18, sextillion=21,
                       septillion=24, octillion=27, nonillion=30, decillion=33, undecillion=36, duodecillion=39,
                       tredecillion=42, quattuordecillion=45, quindecillion=48, sexdecillion=51, septendecillion=54,
                       octodecillion=57, novemdecillion=60, vigintillion=63)

_ordinal_pow_10 = _NumberName()
# noinspection PyInterpreter
_ordinal_pow_10.add_names(thousandth=3, millionth=6, billionth=9, trillionth=12, quadrillionth=18, sextillionth=21,
                       septillionth=24, octillionth=27, nonillionth=30, decillionth=33, undecillionth=36, duodecillionth=39,
                       tredecillionth=42, quattuordecillionth=45, quindecillionth=48, sexdecillionth=51, septendecillionth=54,
                       octodecillionth=57, novemdecillionth=60, vigintillionth=63)

_tens_names = _NumberName()
_tens_names.add_names(twenty=20, thirty=30, forty=40, fifty=50, sixty=60, seventy=70, eighty=80, ninety=90)

_ordinal_tens = _NumberName()
_ordinal_tens.add_names(twentieth=20, thirtieth=30, fortieth=40, fiftieth=50, sixtieth=60, seventieth=70, eightieth=80,
                       ninetieth=90)

_ones_teens = _NumberName()
_ones_teens.add_names(zero=0, one=1, two=2, three=3, four=4, five=5, six=6, seven=7, eight=8, nine=9, ten=10,
                     eleven=11, twelve=12, thirteen=13, fourteen=14, fifteen=15, sixteen=16, seventeen=17,
                     eighteen=18, nineteen=19)

_ordinal_ones_teens = _NumberName()
_ordinal_ones_teens.add_names(zeroth=0, first=1, second=2, third=3, fourth=4, fifth=5, sixth=6, seventh=7, eighth=8,
                             ninth=9, tenth=10, eleventh=11, twelfth=12, thirteenth=13, fourteenth=14, fifteenth=15,
                             sixteenth=16, seventeenth=17, eighteenth=18, nineteenth=19)

def _hundreds_str(num, and_sep=False, ordinal=False):
    if not isinstance(num, int):
        raise TypeError("num must be an int")
    elif num < 0 or num > 999:
        raise ValueError("num must be between 0 and 999")
    if not isinstance(ordinal, bool):
        raise TypeError("ordinal must be a boolean")

    if ordinal and num % 100 == 0:
        hundred_str = "hundredth"
    else:
        hundred_str = "hundred"

    if ordinal and num % 10 == 0:
        this_tens = _ordinal_tens
    else:
        this_tens = _tens_names

    if ordinal:
        this_ones_teens = _ordinal_ones_teens
    else:
        this_ones_teens = _ones_teens

    if and_sep:
        sep = " and "
    else:
        sep = " "

    str_out = ""

    hundreds = int(num/100)
    if hundreds > 0:
        str_out += _ones_teens.value_name(hundreds) + " " + hundred_str
        spacer_string = sep
    else:
        spacer_string = ""

    tens = num % 100
    if tens < 20:
        if hundreds == 0 or tens > 0:
            # Don't add "zero" to the end of non-zero numbers ending in zero
            str_out += spacer_string + this_ones_teens.value_name(tens)
    else:
        ones = num % 10
        tens = 10 * int(tens/10)
        str_out += spacer_string + this_tens.value_name(tens)
        if ones != 0:
            str_out += "-" + this_ones_teens.value_name(ones)

    return str_out

def _am_i_last(curr_index, n10s):
    """
    Determine if the current number is the last non-zero number in the powers of 10 to represent
    :param n10s: the list of values for each three powers of ten in descending order, i.e. billions,
    millions, thousand
    :return: True if the current index is the last non-zero number, False otherwise
    """
    for i in range(curr_index+1, len(n10s)):
        if n10s[i] != 0:
            return False

    return True

def _stringify(num, comma_sep=False, and_sep=False, ordinal='no'):
    """
    Returns a text representation of the number given, internal method called by the external interfaces.
    :param num: the number to represent, currently only integers permitted (positive or negative)
    :param comma_sep: boolean (default False), whether commas should be included every three powers of ten, i.e.
    "one thousand one hundred" or "one thousand, one hundred"
    :param and_sep: boolean (default False), whether "and" should be included between the hundreds and tens/ones
    of each three powers of 10, i.e. "three hundred ten" vs. "three hundred and ten", or "five hundred one" vs.
    "five hundred and one".
    :param ordinal: string (default 'no'), controls whether the number returned is a cardinal number (i.e. "one",
    "two") or an ordinal number ("first", "second"). If set to 'last', only the very last number in the string will
    be an ordinal, i.e. "one hundred ten thousand and eleventh". If set to 'all', each group of three powers of ten
    will have the final part made an ordinal number, i.e. "one hundred ten thousandth and eleventh".
    :return: string, the text representation
    """
    ##################
    # Input checking #
    ##################
    if not isinstance(num, int):
        raise TypeError('num must be an int')
    if not isinstance(comma_sep, bool):
        raise TypeError('comma_sep must be a boolean')
    if not isinstance(and_sep, bool):
        raise TypeError('and_sep must be a boolean')
    if not isinstance(ordinal, str):
        raise TypeError('ordinal must be a string')

    ordinal = ordinal.lower()
    allowed_ordinal_vals = ('no', 'last', 'all')
    if ordinal not in allowed_ordinal_vals:
        raise ValueError('ordinal must be one of the strings: {}'.format(', '.join(allowed_ordinal_vals)))

    if ordinal == 'all':
        this_pow_10 = _ordinal_pow_10
    else:
        this_pow_10 = _powers_of_10

    sub_ordinal = False

    num_str = ""
    if comma_sep:
        sep = ", "
    else:
        sep = " "

    # Split up the number into three digit components, i.e. 0-999, 1000-9999, etc.
    if num < 0:
        neg_string = 'negative '
        num = abs(num)
    else:
        neg_string = ''

    if num == 0:
        if ordinal:
            _ordinal_ones_teens.value_name(0)
        else:
            return _ones_teens.value_name(0)

    p10_max = int(math.log10(num))
    p10s = [x for x in range(0, p10_max+1, 3)]
    p10s.reverse()
    n10s = [int((num % 10**(p + 3))/10**p) for p in p10s]
    for i in range(len(p10s)):
        p = p10s[i]
        n10 = n10s[i]
        if n10 == 0:
            continue
        elif ordinal != 'no' and _am_i_last(i, n10s):
            this_pow_10 = _ordinal_pow_10
            sub_ordinal = True

        # Do not add the separator the first time through
        # Also do not put a comma after the thousands if the
        # ones place is not at least 100
        if p != p10s[0]:
            if p == 0 and n10 < 100:
                if and_sep:
                    num_str += " and "
                else:
                    num_str += " "
            else:
                num_str += sep

        this_str = _hundreds_str(n10, and_sep=and_sep, ordinal=sub_ordinal)
        num_str += this_str
        if p > 0:
            num_str += " " + this_pow_10.value_name(p)

    return neg_string + num_str


def cardinal_number(num, comma_sep=False, and_sep=False):
    """
    Convert an integer into a string representation as an cardinal number (i.e. one, two, etc.)
    :arg num: the number (as an int) to make into a cardinal number string
    :param comma_sep: boolean (default False), whether commas should be included every three powers of ten, i.e.
    "one thousand one hundred" or "one thousand, one hundred"
    :param and_sep: boolean (default False), whether "and" should be included between the hundreds and tens/ones
    of each three powers of 10, i.e. "three hundred ten" vs. "three hundred and ten", or "five hundred one" vs.
    "five hundred and one".
    """
    return _stringify(num, comma_sep=comma_sep, and_sep=and_sep, ordinal='no')


def ordinal_number(num, comma_sep=False, and_sep=False, all_ordinal=False):
    """
    Convert an integer into a string representation as an ordinal number (i.e. first, second, etc.)
    :arg num: the number (as an int) to make into a cardinal number string
    :param comma_sep: boolean (default False), whether commas should be included every three powers of ten, i.e.
    "one thousand one hundredth" or "one thousand, one hundredth"
    :param and_sep: boolean (default False), whether "and" should be included between the hundreds and tens/ones
    of each three powers of 10, i.e. "three hundred tenth" vs. "three hundred and tenth", or "five hundred first" vs.
    "five hundred and first".
    :param all_ordinal: boolean (default False), if False, only the very last number in the string will be an
    ordinal, i.e. "one hundred ten thousand and eleventh". If True, each group of three powers of ten will have
    the final part made an ordinal number, i.e. "one hundred ten thousandth and eleventh".
    """
    if all_ordinal:
        ord_arg = 'all'
    else:
        ord_arg = 'last'

    return _stringify(num, comma_sep=comma_sep, and_sep=and_sep, ordinal=ord_arg)


def repeat_number(num, comma_sep=False, and_sep=False):
    """
    Convert an integer into a string representation as an repeat number (i.e. once, twice, thrice; above 3 it just
    returns "four times", "five times" etc.
    :arg num: the number (as an int) to make into a cardinal number string
    :param comma_sep: boolean (default False), whether commas should be included every three powers of ten, i.e.
    "one thousand one hundred times" or "one thousand, one hundred times"
    :param and_sep: boolean (default False), whether "and" should be included between the hundreds and tens/ones
    of each three powers of 10, i.e. "three hundred ten times" vs. "three hundred and ten times", or "five hundred
    one times" vs. "five hundred and one times".
    """
    if num == 1:
        return "once"
    elif num == 2:
        return "twice"
    elif num == 3:
        return "thrice"
    else:
        return _stringify(num, comma_sep=comma_sep, and_sep=and_sep, ordinal=False) + " times"