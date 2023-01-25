#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 13:38:55 2023

@author: shane
"""
import math
import sys

from pong.matchups import eval_singles

if __name__ == "__main__":

    # Parse player names
    players = sys.argv[1:]
    N_PLAYERS = len(players)
    assert N_PLAYERS > 1, "Needs at least two players"

    # Print meta-data
    N_PAIRS = math.comb(N_PLAYERS, 2)
    print(f"Evaluating {N_PAIRS} match ups...")

    # Print match up predictions
    for i1 in range(N_PLAYERS):
        player1 = players[i1]
        for i2 in range(i1 + 1, N_PLAYERS):
            player2 = players[i2]
            eval_singles(player1, player2)
