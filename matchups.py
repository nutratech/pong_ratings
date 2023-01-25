#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 13:38:55 2023

@author: shane
"""
import math
import os
import sys

from pong.matchups import build_players, eval_singles
from singles import print_singles_matchups

if __name__ == "__main__":

    # Parse player names
    # NOTE: either pass in on command line or set in .env file
    players = sys.argv[1:] or os.environ["PLAYERS"]
    N_PLAYERS = len(players)
    assert N_PLAYERS > 1, "Needs at least two players"

    # Print meta-data
    N_PAIRS = math.comb(N_PLAYERS, 2)
    print(f"Evaluating {N_PAIRS} match ups...")

    # Load players/ratings from CSV
    singles_players, doubles_players = build_players()

    # Print the table first
    # NOTE: convoluted way to sort players in order of descending strength...
    #   iterating over single_players first, which IS sorted already
    print_singles_matchups(
        players=[player for name, player in singles_players.items() if name in players]
    )

    # Print match-up predictions
    for i1 in range(N_PLAYERS):
        player1 = players[i1]

        for i2 in range(i1 + 1, N_PLAYERS):
            player2 = players[i2]

            eval_singles(player1, player2, singles_players)
