from __future__ import print_function
import math
import pdb

# TODO: fix ordinal numbers so that only the last part of the number is ordinal (i.e. not "one hundredth seventieth-fifth")
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

    if ordinal:
        hundred_str = "hundredth"
        this_ones_teens = _ordinal_ones_teens
        this_tens = _ordinal_tens
    else:
        hundred_str = "hundred"
        this_ones_teens = _ones_teens
        this_tens = _tens_names

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

def _stringify(num, comma_sep=False, and_sep=False, ordinal=False):
    """
    Returns a text representation of the number given
    :param num: the number to represent, float or int
    :return: string, the text representation
    """

    if ordinal:
        this_ones_teens = _ordinal_ones_teens
        this_tens = _ordinal_tens
        this_pow_10 = _ordinal_pow_10
    else:
        this_ones_teens = _ones_teens
        this_tens = _tens_names
        this_pow_10 = _powers_of_10

    num_str = ""
    if comma_sep:
        sep = ", "
    else:
        sep = " "

    # Split up the number into three digit components, i.e. 0-999, 1000-9999, etc.
    num = abs(num)
    if num == 0:
        return this_ones_teens.value_name(0)

    p10_max = int(math.log10(num))
    p10s = [x for x in range(0, p10_max+1, 3)]
    p10s.reverse()
    for p in p10s:
        n10 = int((num % 10**(p + 3))/10**p)
        if n10 == 0:
            continue

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

        this_str = _hundreds_str(n10, and_sep=and_sep, ordinal=ordinal)
        num_str += this_str
        if p > 0:
            num_str += " " + this_pow_10.value_name(p)

    return num_str


def cardinal_number(num, comma_sep=False, and_sep=False):
    return _stringify(num, comma_sep=comma_sep, and_sep=and_sep, ordinal=False)


def ordinal_number(num, comma_sep=False, and_sep=False):
    return _stringify(num, comma_sep=comma_sep, and_sep=and_sep, ordinal=True)


def repeat_number(num, comma_sep=False, and_sep=False):
    if num == 1:
        return "once"
    elif num == 2:
        return "twice"
    elif num == 3:
        return "thrice"
    else:
        return _stringify(num, comma_sep=comma_sep, and_sep=and_sep, ordinal=False) + " times"