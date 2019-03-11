#!/usr/bin/env python3

import os
from collections import namedtuple


def get_rulesets(file_pattern, rulesets_dir):
    """
    Applies logical questions to determine what the proper answer is.
    Returns a template to be rendered with the addresses data.

    @param file_pattern: contents of email as string
    @type text: str

    @param rulesets: rules for choosing and excluding a template for answer
    @type rulesets: dict

    @return: list of namedtuples with nice names from files
    @rtype: list of namedtuple
    """

    files = _find_files(file_pattern, rulesets_dir)
    if not files:
        raise FileNotFoundError("Rulesets files could not be located.")

    rulesets = []
    for f in files:
        if f.lower().endswith('csv'):
            import csv
            with open(f, 'r') as con:
                csv_iter = csv.reader(con)
                for line in csv_iter:
                    rulesets.append(line)

        if f.lower().endswith('xlsx'):
            # raise Exception('Implement reading of xlsx files')
            import openpyxl as ox
            print('Opening workbook...')
            wb = ox.load_workbook(f)
            sheet = wb['rulesets']
            # print('Reading rows...')
            for row in range(1, len(sheet['A']) + 1):
                rulesets.append([cell.value for cell in sheet[row]])

    Ruleset = namedtuple('Ruleset', rulesets[0])
    rulesets = [Ruleset(*t) for t in rulesets[1:]]
    if 'template_file' not in rulesets[0]:
        Warning('Please consider naming the column containing template '
                'file names: "template_file"')
    return rulesets


def _find_files(string, path):
    assert isinstance(string, str)
    found_files = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if string in f:
                found_files.append(os.path.join(root, f))
    return found_files
