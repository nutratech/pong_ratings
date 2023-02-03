# -*- coding: utf-8 -*-
"""
Created on Fri 13 Jan 2023 01∶14∶59 PM EST

@author: shane
Shared utilities by both singles and doubles interface
"""
import csv
import os
import sys
from io import StringIO
from typing import Dict, List

import requests

from pong import (
    CSV_GAMES_DOUBLES,
    CSV_GAMES_SINGLES,
    DOUBLES,
    DOUBLES_CSV_URL,
    PROJECT_ROOT,
    SINGLES,
    SINGLES_CSV_URL,
)
from pong.env import PLAYERS_PRESENT
from pong.models import Player


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
    if response.status_code != 200:
        sys.exit(f"Wrong status code, {response.status_code}")

    return bytes(response.content)


def cache_csv_file(_csv_bytes_output: bytes, singles: bool) -> None:
    """
    Persists the CSV file into the git commit history.
    Fall back calculation in case sheets.google.com is unreachable.
    (Manually) verify no nefarious edits are made.
    """
    csv_path = CSV_GAMES_SINGLES if singles else CSV_GAMES_DOUBLES
    with open(csv_path, "wb") as _file:
        _file.write(_csv_bytes_output)


def build_csv_reader(singles: bool) -> csv.DictReader:
    """Returns a csv.reader() object"""

    try:
        url = SINGLES_CSV_URL if singles else DOUBLES_CSV_URL
        _csv_bytes_output = get_google_sheet(url)
        _csv_file = StringIO(_csv_bytes_output.decode())
        cache_csv_file(_csv_bytes_output, singles=singles)

        reader = csv.DictReader(_csv_file)
        reader.fieldnames = [field.strip().lower() for field in reader.fieldnames or []]
        return reader

    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.ReadTimeout,
    ) as err:
        print(repr(err))
        print()
        print("WARN: failed to fetch Google sheet, falling back to cached CSV files...")
        csv_path = CSV_GAMES_SINGLES if singles else CSV_GAMES_DOUBLES

        # pylint: disable=consider-using-with
        reader = csv.DictReader(open(csv_path, encoding="utf-8"))
        reader.fieldnames = [field.strip().lower() for field in reader.fieldnames or []]
        return reader


def get_or_create_player_by_name(players: Dict[str, Player], username: str) -> Player:
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
    print()


def print_subtitle(subtitle: str) -> None:
    """Print a subtitle"""
    print()
    print(subtitle)
    print("~" * len(subtitle))
    print()


def filter_players(_sorted_players: List[Player]) -> List[Player]:
    """Shared method for singles and doubles (main method)"""

    # Filter if requested
    if PLAYERS_PRESENT:
        _sorted_players = list(
            filter(lambda x: x.username in PLAYERS_PRESENT, _sorted_players)
        )

    return _sorted_players


def add_club(_player: Player, club: str, mode: str) -> None:
    """Adds a club tally to the club appearances dictionary"""
    _appearances = _player.club_appearances[mode]

    if club in _appearances:
        _appearances[club] += 1
    else:
        _appearances[club] = 1


def cache_ratings_csv_file(sorted_players: List[Player], singles: bool) -> None:
    """Saves the ratings in a CSV file, so we can manually calculate match ups"""

    # TODO: support p.rating(singles=singles)?
    if singles:
        _file_path = os.path.join(PROJECT_ROOT, "data", "ratings_singles.csv")
        headers = ["username", "mu", "phi", "sigma", "history"]
        _series = [
            (
                p.username,
                p.rating_singles.mu,
                p.rating_singles.phi,
                p.rating_singles.sigma,
                [round(x.mu) for x in p.ratings[SINGLES]],
            )
            for p in sorted_players
        ]
    else:
        _file_path = os.path.join(PROJECT_ROOT, "data", "ratings_doubles.csv")
        headers = ["username", "mu", "sigma", "history"]
        _series = [
            (  # type: ignore
                p.username,
                p.rating_doubles.mu,
                p.rating_doubles.sigma,
                [round(x.mu, 1) for x in p.ratings[DOUBLES]],
            )
            for p in sorted_players
        ]

    # Write the rows
    with open(_file_path, "w", encoding="utf-8") as _f:
        csv_writer = csv.writer(_f)

        csv_writer.writerow(headers)
        csv_writer.writerows(_series)
