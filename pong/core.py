# -*- coding: utf-8 -*-
"""
Created on Fri 13 Jan 2023 01∶14∶59 PM EST

@author: shane
Shared utilities by both singles and doubles interface
"""
import csv
import os
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

    # Filter if requested
    if PLAYERS_PRESENT:
        _sorted_players = list(
            filter(lambda x: x.username in PLAYERS_PRESENT, _sorted_players)
        )

    return _sorted_players


def cache_ratings_csv_file(sorted_players: List[Player], singles=True) -> None:
    """Saves the ratings in a CSV file, so we can manually calculate match ups"""

    # TODO: support p.rating(singles=singles)?
    if singles:
        _file_path = os.path.join(PROJECT_ROOT, "data", "ratings_singles.csv")
        headers = ["username", "mu", "phi", "sigma"]
        _series = [
            (
                p.username,
                p.rating_singles.mu,
                p.rating_singles.phi,
                p.rating_singles.sigma,
            )
            for p in sorted_players
        ]
    else:
        _file_path = os.path.join(PROJECT_ROOT, "data", "ratings_doubles.csv")
        headers = ["username", "mu", "sigma"]
        _series = [
            (
                p.username,
                p.rating_doubles.mu,
                p.rating_doubles.sigma,
            )
            for p in sorted_players
        ]

    # Write the rows
    with open(_file_path, "w", encoding="utf-8") as _f:
        csv_writer = csv.writer(_f)

        csv_writer.writerow(headers)
        csv_writer.writerows(
            [
                (
                    p.username,
                    p.rating_singles.mu,
                    p.rating_singles.phi,
                    p.rating_singles.sigma,
                )
                for p in sorted_players
            ]
        )
