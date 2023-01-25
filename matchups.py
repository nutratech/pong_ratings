#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 13:38:55 2023

@author: shane
"""
import math
import os
import sys

from doubles import print_doubles_matchups
from pong.matchups import build_players, eval_singles
from singles import print_singles_matchups


def print_singles_details() -> None:
    """Prints the details for each requested match-ups"""
    # pylint: disable=invalid-name
    for i1 in range(N_PLAYERS):
        player1 = players[i1]

        for i2 in range(i1 + 1, N_PLAYERS):
            player2 = players[i2]

            eval_singles(player1, player2, singles_players)


def print_doubles_details() -> None:
    """Prints the details for each possible team pairing"""


if __name__ == "__main__":

    # Parse player names
    # NOTE: either pass in on command line or set in .env file
    players = sys.argv[1:] or os.environ["PLAYERS"]
    N_PLAYERS = len(players)
    assert N_PLAYERS > 1, "Needs at least two players"

    singles = int(os.environ["SINGLES"])

    # Print meta-data
    N_PAIRS = math.comb(N_PLAYERS, 2)
    print(f"Evaluating {N_PAIRS} match ups...")

    # Load players/ratings from CSV
    singles_players, doubles_players = build_players()

    # Print the overview table 1st, detail view 2nd
    # NOTE: convoluted way to sort players in order of descending strength...
    #   iterating over single_players first, which IS sorted already
    if singles:
        matchups = print_singles_matchups(
            players=[
                player for name, player in singles_players.items() if name in players
            ]
        )
        print_singles_details(matchups)
    else:
        matchups = print_doubles_matchups(
            players=[
                player for name, player in doubles_players.items() if name in players
            ]
        )
        print_doubles_details(matchups)
