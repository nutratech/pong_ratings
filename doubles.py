#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 23:34:31 2023

@author: shane
"""
from datetime import date

import trueskill
from tabulate import tabulate

from pong.core import (
    DOUBLES_URL,
    build_csv_reader,
    get_or_create_player_by_name,
    print_title,
)
from pong.models import Player


def do_games(
    player1: Player,
    player2: Player,
    player3: Player,
    player4: Player,
    _winners_score: int,
    _losers_score: int,
):
    """
    Updates ratings for given games & players
    NOTE: Team1 = (player1, player2), Team2 = (player3, player4)
    """

    def _update_rating(
        _player1: Player, _player2: Player, _player3: Player, _player4: Player
    ):
        """Updates ratings, player1 is winner and player2 is loser"""

        # Calculate new ratings
        _new_team1_ratings, _new_team2_ratings = trueskill.rate(
            [
                (_player1.rating_doubles, _player2.rating_doubles),
                (_player3.rating_doubles, _player4.rating_doubles),
            ]
        )

        # Assign new ratings
        _player1.rating_doubles = _new_team1_ratings[0]
        _player2.rating_doubles = _new_team1_ratings[1]

        _player3.rating_doubles = _new_team2_ratings[0]
        _player4.rating_doubles = _new_team2_ratings[1]

    # Do the rating updates for won games, then lost games
    #  e.g. 2-1... so 2 wins for the winner, AND then 1 loss for him/her
    # NOTE: do losses come before wins? It influences the ratings slightly
    for _ in range(_losers_score):
        player4.wins_doubles += 1
        player3.wins_doubles += 1
        player2.losses_doubles += 1
        player1.losses_doubles += 1
        _update_rating(player4, player3, player2, player1)

    for _ in range(_winners_score):
        player1.wins_doubles += 1
        player2.wins_doubles += 1
        player3.losses_doubles += 1
        player4.losses_doubles += 1
        _update_rating(player1, player2, player3, player4)


def build_ratings():
    """
    Main method which calculates ratings

    TODO:
     - Support TrueSkill and multiplayer (doubles games) ratings
     - Support an API level interface?
    """

    # Prepare the CSV inputs
    reader = build_csv_reader(DOUBLES_URL)

    players = {}  # Player mapping username -> "class" objects use to store ratings

    # Process the CSV
    for i, row in enumerate(reader):

        # Skip header row
        if i == 0:
            continue

        # Parse fields
        _ = date.fromisoformat(row[0])  # Not used for now
        _winner1 = row[1]
        _winner2 = row[2]

        _loser1 = row[3]
        _loser2 = row[4]

        _winners_score = int(row[5].split("-")[0])
        _losers_score = int(row[5].split("-")[1])

        # Check if players are already tracked, create if not
        _winner_player1 = get_or_create_player_by_name(players, _winner1)
        _winner_player2 = get_or_create_player_by_name(players, _winner2)
        _loser_player1 = get_or_create_player_by_name(players, _loser1)
        _loser_player2 = get_or_create_player_by_name(players, _loser2)

        # Run the algorithm and update ratings
        # NOTE: we're assuming these are singles games only (for now)
        do_games(
            _winner_player1,
            _winner_player2,
            _loser_player1,
            _loser_player2,
            _winners_score,
            _losers_score,
        )

    # Print off rankings
    # TODO: filter inactive or highly uncertain ratings?
    print_title("Doubles rankings")
    sorted_players = sorted(
        players.values(), key=lambda x: x.rating_doubles.mu, reverse=True
    )
    _table = tabulate(
        [
            (x.username, x.str_rating_doubles, f"{x.wins_doubles}-{x.losses_doubles}")
            for x in sorted_players
        ],
        headers=["Username", "Trueskill", "Record"],
    )
    print(_table)

    # Used to build pairings / ideal matches
    return sorted_players


if __name__ == "__main__":
    # NOTE: Also need to support DOUBLES rankings & matches (not just singles)
    print(f"Last updated: {date.today()}")
    _sorted_players = build_ratings()
