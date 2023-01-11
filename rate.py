#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 23:34:31 2023

@author: shane
"""
import csv
import os
from datetime import date
from io import StringIO
from typing import List

import requests
from tabulate import tabulate

from pong.glicko2 import glicko2
from pong.models import Player

# Hardcoded URL value pointing to our sheet
GAMES_URL = (
    "https://docs.google.com/spreadsheet/ccc"
    "?key=1evcgUzJ5hO55RYshc3dH-EmzZfor58t0qPB-zp8iw4A"
    "&output=csv"
)


def get_google_sheet():
    """
    Returns a byte array (string)
    TODO:
      - Cache these on the filesystem, commit, and have the network latency be an
        optional step to "refresh" the data in real time.
        But also allow running instantly on old (cached) CSV files.
      - Support multiple sheets per document (e.g. separate doubles sheet)?
    """

    response = requests.get(GAMES_URL, timeout=12)
    assert response.status_code == 200, "Wrong status code"

    return response.content


def print_title(title: str):
    """Prints a neat and visible header to separate tables"""
    print(os.linesep)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(title)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("")


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
    for _ in range(_loser_score):
        _update_rating(player2, player1)

    for _ in range(_winner_score):
        _update_rating(player1, player2)


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

    def _get_or_create_player_by_name(username: str):
        """Adds a player"""
        if username in players:
            return players[username]

        _player = Player(username)
        players[username] = _player
        return _player

    # Process the CSV
    for i, row in enumerate(reader):

        # Skip header row
        if i == 0:
            continue

        # Parse fields
        _ = date.fromisoformat(row[0])  # Not used for now
        _winner = row[1]
        _loser = row[2]

        _winner_score = int(row[3].split("-")[0])
        _loser_score = int(row[3].split("-")[1])

        # Check if players are already tracked, create if not
        _winner_player = _get_or_create_player_by_name(_winner)
        _loser_player = _get_or_create_player_by_name(_loser)

        # Run the algorithm and update ratings
        # NOTE: we're assuming these are singles games only (for now)
        do_games(_winner_player, _loser_player, _winner_score, _loser_score)

    # Print off rankings
    print_title("Singles rankings")
    sorted_players = sorted(
        players.values(), key=lambda x: x.rating_singles.mu, reverse=True
    )
    _table = tabulate(
        [(x.username, x.str_rating_singles) for x in sorted_players],
        headers=["Username", "Glicko 2"],
    )
    print(_table)

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
    for player1 in players:
        for player2 in players:

            # Can't play yourself
            if player1 == player2:
                continue

            # Don't double count (p1, p2) AND (p2, p1)... they are the same
            if (player2, player1) in already_matched:
                continue

            # Compute quality, and add to list
            quality_of_match = round(
                glicko2.Glicko2().quality_1vs1(
                    player1.rating_singles, player2.rating_singles
                ),
                3,
            )
            matchups.append((player1.username, player2.username, quality_of_match))
            already_matched.add((player1, player2))

    # Print off best 10 matchups
    print_title("Singles matchups")
    matchups.sort(key=lambda x: x[2], reverse=True)

    _table = tabulate(matchups[:10], headers=["Player 1", "Player 2", "Fairness"])
    print(_table)


if __name__ == "__main__":
    # NOTE: Also need to support DOUBLES rankings & matchups (not just singles)
    _sorted_players = build_ratings()
    print_matchups(_sorted_players)
