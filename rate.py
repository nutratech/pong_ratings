#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 23:34:31 2023

@author: shane
"""
import csv
from datetime import date
from io import StringIO
from typing import List

import requests
from glicko2 import glicko2

from models import Player

GAMES_URL = (
    "https://docs.google.com/spreadsheet/ccc"
    "?key=1evcgUzJ5hO55RYshc3dH-EmzZfor58t0qPB-zp8iw4A"
    "&output=csv"
)


def get_google_sheet():
    """
    Returns a byte array (string)
    TODO: Cache these on the filesystem, commit, and have the network latency be an
     optional step to "refresh" the data in real time.
     But also allow running instantly on old (cached) CSV files.
    """

    response = requests.get(GAMES_URL)
    assert response.status_code == 200, "Wrong status code"

    return response.content


def build_players():
    """Creates the player objects with a default rating"""


def do_games(player1: Player, player2: Player, _winner_score: int, _loser_score: int):
    """Updates ratings for given games & players"""

    def _update_rating(_player1: Player, _player2: Player):
        """Updates ratings, player1 is winner and player2 is loser"""

        # Calculate new ratings
        _new_player1_rating, _new_player2_rating = _player1.rating_singles.rate_1vs1(
            _player1.rating_singles, _player2.rating_singles
        )

        # Assign new ratings
        _player1.rating_singles.mu = _new_player1_rating.mu
        _player1.rating_singles.phi = _new_player1_rating.phi
        _player1.rating_singles.sigma = _new_player1_rating.sigma

        _player2.rating_singles.mu = _new_player2_rating.mu
        _player2.rating_singles.phi = _new_player2_rating.phi
        _player2.rating_singles.sigma = _new_player2_rating.sigma

    # Do the rating updates for won games, then lost games
    #  e.g. 2-1... so 2 wins for the winner, AND then 1 loss for him/her
    # NOTE: do losses come before wins? It influences the ratings slightly
    for _ in range(_winner_score):
        _update_rating(player1, player2)

    for _ in range(_loser_score):
        _update_rating(player2, player1)


def build_ratings():
    """
    Main method which calculates ratings

    TODO:
     - Support TrueSkill and multiplayer (doubles games) ratings
     - Support an API level interface?
    """

    # Prepare the CSV inputs
    _csv_bytes_output = get_google_sheet()
    _csv_file = StringIO(_csv_bytes_output.decode())
    reader = csv.reader(_csv_file)

    players = {}  # Player mapping username -> "class" objects use to store ratings
    headers = []

    def _get_or_create_player_by_name(username: str):
        """Adds a player"""
        if username in players:
            return players[username]

        _player = Player(username)
        players[username] = _player
        return _player

    # Process the CSV
    for row in reader:

        # Skip header row
        if not headers:
            headers = row
            continue

        # Parse fields
        _date = date.fromisoformat(row[0])
        _winner = row[1]
        _loser = row[2]

        _outcome = row[3].split("-")
        _winner_score = int(_outcome[0])
        _loser_score = int(_outcome[1])

        # Check if players are already tracked
        _winner_player = _get_or_create_player_by_name(_winner)
        _loser_player = _get_or_create_player_by_name(_loser)

        # Run the algorithm and update ratings
        # NOTE: we're assuming these are singles games only (for now)
        do_games(_winner_player, _loser_player, _winner_score, _loser_score)

    sorted_players = sorted(
        players.values(), key=lambda x: x.rating_singles.mu, reverse=True
    )
    for player in sorted_players:
        print(player)

    # Used to build pairings / ideal matchups
    return sorted_players


def print_matchups(players: List[Player]):
    """
    Prints out the fairest possible games, matching up nearly equal opponents for
    interesting play.
    """
    already_matched = set()
    matchups = []

    # Evaluate all possible match ups
    for p1 in players:
        for p2 in players:

            # Can't play yourself
            if p1 == p2:
                continue

            # Don't double count (p1, p2) AND (p2, p1)... they are the same
            if (p2, p1) in already_matched:
                continue

            quality_of_match = round(
                glicko2.Glicko2().quality_1vs1(p1.rating_singles, p2.rating_singles),
                3,
            )

            matchups.append((p1.username, p2.username, quality_of_match))
            already_matched.add((p1, p2))

    # Sort (and print off the top 10)
    matchups.sort(key=lambda x: x[2], reverse=True)

    for match in matchups[:10]:
        print(match)


if __name__ == "__main__":
    _sorted_players = build_ratings()
    print_matchups(_sorted_players)
