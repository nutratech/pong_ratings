#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 13:38:55 2023

@author: shane
"""
import os
import sys
from typing import Dict, List

from doubles import print_doubles_matchups
from pong.env import MODE_SINGLES
from pong.matchups import build_players, eval_doubles, eval_singles
from pong.models import Player
from singles import print_singles_matchups


def print_singles_details(matchups: List[tuple], players: Dict[str, Player]) -> None:
    """Prints the details for each requested match-ups"""
    for pairing in matchups:
        eval_singles(
            pairing[0],
            pairing[1],
            players,
        )


def print_doubles_details(matchups: List[tuple], players: Dict[str, Player]) -> None:
    """Prints the details for each possible team pairing"""
    for pairing in matchups:
        eval_doubles(
            pairing[0],
            pairing[1],
            pairing[2],
            pairing[3],
            players,
            prob_game=pairing[-1],
            quality=pairing[-2],
        )


if __name__ == "__main__":

    # Parse player names
    # NOTE: either pass in on command line or set in .env file
    _players = sys.argv[1:] or os.environ["PONG_PLAYERS"].split()
    N_PLAYERS = len(_players)

    # TODO: support N_PLAYERS = 1, just match that one person with all others
    if N_PLAYERS < 2:
        sys.exit(f"Needs at least two players, got {N_PLAYERS}")

    # Load players/ratings from CSV
    singles_players, doubles_players = build_players()

    # Print the overview table 1st, detail view 2nd
    # NOTE: convoluted way to sort players in order of descending strength...
    #   iterating over single_players first, which IS sorted already
    if MODE_SINGLES:
        singles_matchups = print_singles_matchups(
            players=sorted(
                [singles_players[name] for name in _players],
                key=lambda p: p.rating_singles.mu,
                reverse=True,
            )
        )
        print_singles_details(matchups=singles_matchups, players=singles_players)
    else:
        doubles_matchups = print_doubles_matchups(
            players=sorted(
                [doubles_players[name] for name in _players],
                key=lambda p: p.rating_doubles.mu,
                reverse=True,
            ),
            delta_mu_threshold=15.0,
            two_rd_threshold=15.0,
        )
        if N_PLAYERS < 7:
            print_doubles_details(matchups=doubles_matchups, players=doubles_players)
