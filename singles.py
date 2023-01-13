#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 23:34:31 2023

@author: shane
"""
import math
from datetime import date
from typing import List

from tabulate import tabulate

from pong.core import (
    SINGLES_URL,
    build_csv_reader,
    get_or_create_player_by_name,
    print_title,
)
from pong.glicko2 import glicko2
from pong.models import Player


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
        player2.wins_singles += 1
        player1.losses_singles += 1
        _update_rating(player2, player1)

    for _ in range(_winner_score):
        player1.wins_singles += 1
        player2.losses_singles += 1
        _update_rating(player1, player2)


def build_ratings():
    """
    Main method which calculates ratings

    TODO:
     - Support TrueSkill and multiplayer (doubles games) ratings
     - Support an API level interface?
    """

    # Prepare the CSV inputs
    reader = build_csv_reader(SINGLES_URL)

    players = {}  # Player mapping username -> "class" objects use to store ratings

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
        _winner_player = get_or_create_player_by_name(players, _winner)
        _loser_player = get_or_create_player_by_name(players, _loser)

        # Run the algorithm and update ratings
        # NOTE: we're assuming these are singles games only (for now)
        do_games(_winner_player, _loser_player, _winner_score, _loser_score)

    # Print off rankings
    # TODO: filter inactive or highly uncertain ratings?
    print_title("Singles rankings")
    sorted_players = sorted(
        players.values(), key=lambda x: x.rating_singles.mu, reverse=True
    )
    _table = tabulate(
        [
            (x.username, x.str_rating_singles, f"{x.wins_singles}-{x.losses_singles}")
            for x in sorted_players
        ],
        headers=["Username", "Glicko 2", "Record"],
    )
    print(_table)

    # Used to build pairings / ideal matches
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

    # Print off best matches
    _n_top = 15
    _n_choose_2_players = math.comb(len(players), 2)
    print_title(
        f"Singles matches (top {min(_n_top, _n_choose_2_players)}, "
        f"{len(players)}C2={_n_choose_2_players} possible)"
    )
    matchups.sort(key=lambda x: x[2], reverse=True)

    _table = tabulate(matchups[:_n_top], headers=["Player 1", "Player 2", "Quality"])
    print(_table)


if __name__ == "__main__":
    # NOTE: Also need to support DOUBLES rankings & matches (not just singles)
    print("SINGLES")
    print(f"Last updated: {date.today()}")
    _sorted_players = build_ratings()
    print_matchups(_sorted_players)
