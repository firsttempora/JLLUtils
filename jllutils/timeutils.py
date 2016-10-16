"""
JLLUtils.timeutils: module contains convenience functions for working with dates and times
Includes:
    str2date: converts a string into a datetime.date or datetime.datetime object
    date2str: converts a datetime.date or datetime.datetime object into a string
"""
from __future__ import print_function
from __future__ import division

__author__ = 'Josh'

import datetime as dt
import re
import pdb

# TODO: implement pivot year for two number years

def str2date(str_in, format_in="yyyy-mm-dd", typeout=None):
    """
    Converts the given str (str_in) to a datetime.date or datetime.datetime
    object, using the format optionally given as the parameter format_in.
    :param str_in: The date or time to convert to a date or datetime object,
    input as a string. The string must match the given or default format, with
    the exception of the identifiers AM or PM, which do not need to be included
    in the format. If AM/PM are included, the hour must be between 1 and 12 and
    will be appropriately scaled if PM. Noon is defined as 12 PM, midnight as 12 AM.
    If neither AM nor PM included in the input string (str_in), the hour is assumed
    to be in 24 hour format (0 is midnight, 12 is noon)
    :param format_in: The format of the input string. Defaults to yyyy-mm-dd. An alternate
     format can be specified using the following identifiers:
        yyyy - four number year OR yy - two number year (will assume it to be in the last
            100 years)
        mm - two number month OR mmm - three letter month abbreviation
        dd - two number day
        HH - two number hour
        MM - two number minute
        SS - two number second
    If year is omitted, it defaults to this year. If month or day is omitted, they default
    to 1. If hour, minute, or second are omitted, they default to 0.
    :param typeout: allows the user to specify if the return type should be a datetime.date
    or datetime.datetime object. Must be the type datetime.date or datetime.datetime. If not
    given, a datetime.datetime object is returned unless hour, minute, and second are omitted
    from the format.
    :return: a datetime.date or datetime.datetime object corresponding to the specified year.
    Examples:
        Default format:
        str2date('2016-10-12') returns datetime.date(2016,10,12)

        Two digit years, assuming current year is 2016:
        str2date('10/12/16','mm/dd/yy') returns datetime.date(2016,10,12)
        str2date('10/12/17','mm/dd/yy') returns datetime.date(1917,10,12)


    """
    if type(str_in) is not str:
        raise TypeError("str_in must be a str")
    if type(format_in) is not str:
        raise TypeError("format_in must be a str")
    if typeout is not dt.date and typeout is not dt.datetime and typeout is not None:
        raise TypeError("typeout must be datetime.date, datetime.datetime, or None")

    # Parse the parts of the date (year, month, day, hour, minute, second)
    # Three letter month (Jan, Feb, etc) and two number years need special
    # handling

    # First check if the string AM or PM is present in the input date time string,
    # this will indicate that the hour needs to be adjusted
    ampm_match = re.search("[aApP][mM]", str_in)
    if ampm_match is None:
        hr24_bool = True
    else:
        hr24_bool = False
        ampm_str = ampm_match.group(0).lower()


    # Try finding four number year first (because 'yy' will match 'yyyy' too)
    # If there isn't even a two letter year, set the year to the current one
    yr = __substr_to_int(str_in, format_in, "yyyy")
    if yr == 0:
        yr = __substr_to_int(str_in, format_in, "yy", def_val=None)  # must use None because 00 is a legitimate year
        if yr is None:
            yr = dt.date.today().year
        else:
            curr_yr_tmp = dt.date.today().year
            curr_yr = curr_yr_tmp % 100
            curr_century = curr_yr_tmp - curr_yr
            if yr <= curr_yr:
                yr = yr + curr_century
            else:
                yr = yr + curr_century - 100

    # Similar approach for months, except that for three letter months, we
    # need to convert from name to number. Default to Jan if no month given
    mn = __substr_to_month(str_in, format_in) # always searches for "mmm"
    if mn is None:
        mn = __substr_to_int(str_in, format_in, "mm")
        if mn == 0:
            mn = 1

    # Similar again for day, except that it can only ever be specified as "dd"
    dy = __substr_to_int(str_in, format_in, "dd")
    if dy == 0:
        dy = 1

    # Hour, minute, and second are easier because they can be 0...
    hour = __substr_to_int(str_in, format_in, "HH")
    # ... but hour needs to handle AM/PM. Afternoon needs 12 hours added
    # (1:00 PM = 1300 hr, 8:00 = 2000 hr, etc) but noon should stay 12 and
    # midnight (12 AM) should become hour = 0
    if not hr24_bool:
        if hour < 1 or hour > 12:
            raise ValueError("If using AM/PM format, hour must be between 1 and 12")
        elif hour != 12 and ampm_str == "pm":
            hour += 12
        elif hour == 12 and ampm_str == "am":
            hour = 0
    minute = __substr_to_int(str_in, format_in, "MM")
    second = __substr_to_int(str_in, format_in, "SS")

    # If no type out specified, it will be date only if hour, minute, and second
    # are all 0
    if typeout is None:
        if hour == 0 and minute == 0 and second == 0:
            typeout = dt.date
        else:
            typeout = dt.datetime

    if typeout is dt.date:
        return dt.date(yr, mn, dy)
    elif typeout is dt.datetime:
        return dt.datetime(yr, mn, dy, hour, minute, second)
    else:
        raise RuntimeError("Not implemented: typeout other than datetime.date or datetime.datetime")

def date2str(date_in, format_in="yyyy-mm-dd"):
    if type(date_in) is not dt.date and type(date_in) is not dt.datetime:
        raise TypeError("date_in must be a datetime.date or datetime.datetime")
    if type(format_in) is not str:
        raise TypeError("format_in must be a str")

    ampm_match = re.search("[aApP][mM]", format_in)
    if ampm_match is None:
        ampm_bool = False
    else:
        ampm_bool = True

    # Year again needs to try yyyy first. str.find returns -1 if string not found
    if format_in.find("yyyy") >= 0:
        format_in = format_in.replace("yyyy", "{:04}".format(date_in.year))
    else:
        format_in = format_in.replace("yy", "{:02}".format(date_in.year % 100)) # replace does nothing if match not found

    # Month needs to try mmm first
    if format_in.find("mmm") >= 0:
        format_in = format_in.replace("mmm", __month_abbrev(date_in.month))
    else:
        format_in = format_in.replace("mm", "{:02}".format(date_in.month))

    # Day, hour, minute, and second are easy since they can only be specified one way
    format_in = format_in.replace("dd", "{:02}".format(date_in.day))
    if type(date_in) is dt.datetime:
        # Hour does need to account for AM/PM again though.
        if not ampm_bool:
            date_hr = date_in.hour
        else:
            if date_in.hour >= 12:
                ampm_str = "PM"
                if date_in.hour != 12:
                    date_hr = date_in.hour - 12
                else:
                    date_hr = date_in.hour
            else:
                ampm_str = "AM"
                if date_in.hour == 0:
                    date_hr = 12
                else:
                    date_hr = date_in.hour
            format_in = format_in.replace(ampm_match.group(0), ampm_str)

        format_in = format_in.replace("HH", "{:02}".format(date_hr))
        format_in = format_in.replace("MM", "{:02}".format(date_in.minute))
        format_in = format_in.replace("SS", "{:02}".format(date_in.second))

    return format_in


def __substr_to_int(fullstr, date_format, substr, def_val=0):
    m = re.search(substr, date_format)
    if m is None:
        val = def_val
    else:
        val = int(fullstr[m.start():m.end()])

    return val

def __substr_to_month(fullstr, date_format):
    m = re.search("mmm", date_format)
    if m is None:
        val = None
    else:
        val = __month_abbrev(fullstr[m.start():m.end()])

    return val

def __month_abbrev(month_in):
    abbrevs = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    if type(month_in) is str:
        try:
            i = abbrevs.index(month_in.lower())
        except ValueError as err:
            raise ValueError("Month abbreviation {0} not recognized".format(month_in))

        return i+1
    elif type(month_in) is int:
        if month_in < 1 or month_in > 12:
            raise ValueError("Numerical month must be between 1 and 12")

        return abbrevs[month_in-1].capitalize()
    else:
        raise TypeError("month_in must be a str or int")