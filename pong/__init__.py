# -*- coding: utf-8 -*-
"""
Created on Tue 10 Jan 2023 12∶39∶06 PM EST

@author: shane
"""
import math
import os

from pong.env import PONG_SHEET_GID_DOUBLES, PONG_SHEET_GID_SINGLES, PONG_SHEET_KEY

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Enum
SINGLES = "singles"
DOUBLES = "doubles"

# Constants
DRAW_PROB_DOUBLES = math.comb(20, 10) * (1 / 2) ** 20


def _url(gid: int) -> str:
    """Hard-coded URL values pointing to our sheet"""

    return (
        "https://docs.google.com/spreadsheet/ccc"
        f"?key={PONG_SHEET_KEY}"
        f"&gid={gid}"
        "&output=csv"
    )


# URLs to google sheets for singles & doubles CSVs
CSV_GAMES_URLS = {
    SINGLES: _url(PONG_SHEET_GID_SINGLES),
    DOUBLES: _url(PONG_SHEET_GID_DOUBLES),
}

# Fall back (cached CSV files, if sheets.google.com is unreachable)
CSV_GAMES_FILE_PATHS = {
    SINGLES: os.path.join(PROJECT_ROOT, "data", "games_singles.csv"),
    DOUBLES: os.path.join(PROJECT_ROOT, "data", "games_doubles.csv"),
}

# Persist ratings after main script for auxiliary calculations
CSV_RATINGS_FILE_PATHS = {
    SINGLES: os.path.join(PROJECT_ROOT, "data", "ratings_singles.csv"),
    DOUBLES: os.path.join(PROJECT_ROOT, "data", "ratings_doubles.csv"),
}
