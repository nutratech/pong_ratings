# -*- coding: utf-8 -*-
"""
Created on Fri 13 Jan 2023 01∶14∶59 PM EST

@author: shane
Shared utilities by both singles and doubles interface
"""
import csv
import os
from datetime import datetime
from io import StringIO
from typing import List

import requests

from pong.env import PLAYERS_PRESENT
from pong.models import Player


# Hard-coded URL values pointing to our sheet
def _url(gid: int) -> str:
    _spreadsheet_key = "1evcgUzJ5hO55RYshc3dH-EmzZfor58t0qPB-zp8iw4A"
    return (
        "https://docs.google.com/spreadsheet/ccc"
        f"?key={_spreadsheet_key}"
        f"&gid={gid}"
        "&output=csv"
    )


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

SINGLES_URL = _url(834797930)
DOUBLES_URL = _url(682349527)

# Fall back (cached CSV files, if sheets.google.com is unreachable)
SINGLES_CSV = os.path.join(PROJECT_ROOT, "data", "games_singles.csv")
DOUBLES_CSV = os.path.join(PROJECT_ROOT, "data", "games_doubles.csv")


def get_google_sheet(url: str) -> bytes:
    """
    Returns a byte array (string)
    TODO:
      - Cache these on the filesystem, commit, and have the network latency be an
        optional step to "refresh" the data in real time.
        But also allow running instantly on old (cached) CSV files.
      - Support multiple sheets per document (e.g. separate "doubles games" sheet)?
    """

    response = requests.get(url, timeout=2)
    assert response.status_code == 200, "Wrong status code"

    return response.content


def cache_csv_file(_csv_bytes_output, singles=True) -> None:
    """
    Persists the CSV file into the git commit history.
    Fall back calculation in case sheets.google.com is unreachable.
    (Manually) verify no nefarious edits are made.
    """
    csv_path = SINGLES_CSV if singles else DOUBLES_CSV
    with open(csv_path, "wb") as _file:
        _file.write(_csv_bytes_output)


def build_csv_reader(singles=True) -> csv.reader:
    """Returns a csv.reader() object"""

    try:
        url = SINGLES_URL if singles else DOUBLES_URL
        _csv_bytes_output = get_google_sheet(url)
        _csv_file = StringIO(_csv_bytes_output.decode())
        cache_csv_file(_csv_bytes_output, singles=singles)

        return csv.reader(_csv_file)

    except requests.exceptions.ConnectionError as err:
        print(repr(err))
        print()
        print("WARN: failed to fetch Google sheet, falling back to cached CSV files...")
        csv_path = SINGLES_CSV if singles else DOUBLES_CSV

        return csv.reader(open(csv_path, encoding="utf-8"))


def get_or_create_player_by_name(players: dict, username: str) -> Player:
    """Adds a player"""
    if username in players:
        return players[username]

    _player = Player(username)
    players[username] = _player
    return _player


def print_title(title: str) -> None:
    """Prints a neat and visible header to separate tables"""
    print(os.linesep)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(title)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("")


def filter_players(_sorted_players: List[Player]) -> List[Player]:
    """Shared method for singles and doubles (main method)"""
    print("SINGLES")
    print(f"Last updated: {datetime.utcnow()}")

    # Filter if requested
    if PLAYERS_PRESENT:
        _sorted_players = list(
            filter(lambda x: x.username in PLAYERS_PRESENT, _sorted_players)
        )

    return _sorted_players
