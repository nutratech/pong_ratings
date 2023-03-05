#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 15:23:06 2023

@author: shane
"""
import csv

import requests

from pong import CLI_CONFIG


def get_google_sheet(url: str) -> bytes:
    """
    Returns a byte array (string) of the Google Sheet in CSV format
    """
    print(f"GET '{url}'\\")

    response = requests.get(url, timeout=2)
    response.raise_for_status()

    return bytes(response.content)


def cache_csv_games_file(_csv_bytes_output: bytes, _file_path: str) -> None:
    """
    Persists the CSV file into the git commit history.
    Fall back calculation in case sheets.google.com is unreachable.
    (Manually) verify no nefarious edits are made.
    """
    print(f" >'{_file_path}'")
    with open(_file_path, "wb") as _file:
        _file.write(_csv_bytes_output)


def build_csv_reader(csv_file_path: str) -> csv.DictReader:
    """Returns a csv.reader() object"""
    if CLI_CONFIG.debug:
        print(f"Using csv_file_path='{csv_file_path}'")

    # pylint: disable=consider-using-with
    reader = csv.DictReader(open(csv_file_path, encoding="utf-8"))
    return reader
