# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 17:14:19 2023

@author: shane
Loads ENVIRONMENT VARIABLES from file: `.env`
"""
import os

import dotenv

from pong import DOUBLES, SINGLES

dotenv.load_dotenv(verbose=True)

# TODO: store spreadsheet key and gid in .env file?

# TODO: support inverse too? Inactive players
PLAYERS_PRESENT = set()
if os.environ.get("PONG_PLAYERS"):
    PLAYERS_PRESENT = set((os.environ.get("PONG_PLAYERS") or str()).split())

MODE_SINGLES = not int(os.environ.get("PONG_DOUBLES") or 0)

PONG_SHEET_KEY = os.environ["PONG_SHEET_KEY"]
PONG_SHEET_GID_SINGLES = int(os.environ["PONG_SHEET_GID_SINGLES"])
PONG_SHEET_GID_DOUBLES = int(os.environ["PONG_SHEET_GID_DOUBLES"])


# URLs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _url(gid: int) -> str:
    """Hard-coded URL values pointing to our sheet"""

    return (
        "https://docs.google.com/spreadsheet/ccc"
        f"?key={PONG_SHEET_KEY}"
        f"&gid={gid}"
        "&output=csv"
    )


# URLs to Google Sheets for singles & doubles CSVs
CSV_GAMES_URLS = {
    SINGLES: _url(PONG_SHEET_GID_SINGLES),
    DOUBLES: _url(PONG_SHEET_GID_DOUBLES),
}
