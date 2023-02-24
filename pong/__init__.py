# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 12:24:55 2023

@author: shane
"""
import argparse
import math
import os
import shutil

from pong.env import PONG_SHEET_GID_DOUBLES, PONG_SHEET_GID_SINGLES, PONG_SHEET_KEY

# Package info
__title__ = "pr"
__version__ = "0.0.1.dev12"
__author__ = "Shane J"
__email__ = "chown_tee@proton.me"
__license__ = "GPL v3"
__copyright__ = "Copyright 2022-2023 Shane J"
__url__ = "https://github.com/nutratech/pong_ratings"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Other constants
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Global variables
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Console size, don't print more than it
BUFFER_WD = shutil.get_terminal_size()[0]
BUFFER_HT = shutil.get_terminal_size()[1]

# Location on disk to cache CSV file
CSV_GAMES_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "games.csv")

# lichess.org uses 110 and 75 (65 for variants)
DEVIATION_PROVISIONAL = 110
DEVIATION_ESTABLISHED = 75

# Mathematical constants
DRAW_PROB_DOUBLES = math.comb(20, 10) * (1 / 2) ** 20


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Enums
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Game types
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SINGLES = "singles"
DOUBLES = "doubles"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# URLs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLI config (settings, defaults, and flags)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# pylint: disable=too-few-public-methods,too-many-instance-attributes
class CliConfig:
    """Mutable global store for configuration values"""

    def __init__(self, debug: bool = False) -> None:
        self.debug = debug

    def set_flags(self, args: argparse.Namespace) -> None:
        """
        Sets flags:
          {DEBUG, PAGING}
            from main (after arg parse). Accessible throughout package.
            Must be re-imported globally.
        """

        self.debug = args.debug

        if self.debug:
            print(f"Console size: {BUFFER_HT}h x {BUFFER_WD}w")


# Create the shared instance object
CLI_CONFIG = CliConfig()
