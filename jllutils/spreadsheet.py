from __future__ import print_function

import re
import xlrd

import pdb

def save_range_as_csv(xls_file, cell_range, output_file, sheet=0, delim=',', skip_empty='none'):
    """
    Save a subset of an Excel file to a csv file. You could do this with Visual Basic, but, uh, no thanks.
    :param xls_file: the path to the Excel file to read
    :param cell_range: a list or tuple of cell names (e.g. ['A1', 'G5'] giving the upper left corner and the lower right
     corner of the range of cells to export.
    :param output_file: the file to save the csv as. Will be overwritten if it exists.
    :param sheet: which sheet to use. May be an index (0 based, default is 0) or by name.
    :param delim: the character to use for delimiting data in the output file. Default is a comma.
    :param skip_empty: how to deal with empty cells. See docstring for iter_cell_range for values.
    :return: none
    """
    with open(output_file, 'w') as fobj:
        for line_list in iter_cell_range(xls_file=xls_file, cell_range=cell_range, sheet=sheet, skip_empty=skip_empty):
            line = delim.join(line_list) + '\n'
            fobj.write(line)


def read_range(xls_file, cell_range, sheet=0, skip_empty='none'):
    """
    Reads a range of cells from an Excel file and returns their values as a list-of-lists. This is basically a
    convenience function for [l for l in iter_cell_range()]
    :param xls_file: the path to the Excel file to read
    :param cell_range: a list or tuple of cell names (e.g. ['A1', 'G5'] giving the upper left corner and the lower right
     corner of the range of cells to export.
    :param sheet: which sheet to use. May be an index (0 based, default is 0) or by name.
    :param skip_empty: how to deal with empty cells. See docstring for iter_cell_range for values.
    :return: list-of-lists of cell values. The inner lists represent rows.
    """

    return [l for l in iter_cell_range(xls_file=xls_file, cell_range=cell_range, sheet=sheet, skip_empty=skip_empty)]


def iter_cell_range(xls_file, cell_range, sheet=0, skip_empty='none'):
    """
    Iterate over lines in a cell range of an Excel file.
    :param xls_file: the path to the Excel file to read
    :param cell_range: a list or tuple of cell names (e.g. ['A1', 'G5'] giving the upper left corner and the lower right
     corner of the range of cells to export.
    :param sheet: which sheet to use. May be an index (0 based, default is 0) or by name.
    :param skip_empty: how to deal with empty cells. May be 'none' (default, don't skip them), 'any' (skips any empty
    cells), 'row' (not implemented, would only skip if a whole row is empty), 'col' (not implemented, would only skip if
    a whole column is empty), 'rowcol' (not implemented, would skip if either a whole row or whole column was empty).
    :return: generator that iterates over rows.
    """

    with xlrd.open_workbook(xls_file) as xobj:
        if isinstance(sheet, int):
            sheet_obj = xobj.sheet_by_index(sheet)
        elif isinstance(sheet, str):
            sheet_obj = xobj.sheet_by_name(sheet)
        else:
            TypeError('sheet must be a string or an int')

    start_cell_ind = _cell_to_ind(cell_range[0])
    end_cell_ind = _cell_to_ind(cell_range[1])

    for r in range(start_cell_ind[0], end_cell_ind[0] + 1):
        if skip_empty.lower() == 'any':
            line_list = [c.value for c in sheet_obj.row_slice(r, start_cell_ind[1], end_cell_ind[1] + 1) if
                         len(c.value) > 0]
        else:
            line_list = [c.value for c in sheet_obj.row_slice(r, start_cell_ind[1], end_cell_ind[1] + 1)]

        if skip_empty.lower() == 'any' and len(line_list) == 0:
            continue

        yield line_list


def _cell_to_ind(cell):
    """
    Converts an Excel cell index to a tuple
    :param cell: The cell index as a string (i.e. 'A1')
    :return: tuple of indices that will refer to that cell: (row, col)
    """

    map_str = 'ABCDEFGHIJKLNMOPQRSTUVWXYZ'
    col_ind = 0
    p26 = 1

    col_name = re.match('[a-zA-Z]+', cell).group().upper()
    for letter in reversed(col_name):
        col_ind += map_str.index(letter) * p26
        p26 *= 26

    row_ind = int(re.search('[0-9]+', cell).group())-1

    return (row_ind, col_ind)