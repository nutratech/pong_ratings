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
from pong.matchups import build_players, eval_doubles, eval_singles
from pong.models import Player
from singles import print_singles_matchups


def print_singles_details(matchups: List[tuple], players: Dict[str, Player]) -> None:
    """Prints the details for each requested match-ups"""
    for matchup in matchups:
        eval_singles(
            matchup[0],
            matchup[1],
            players,
        )


def print_doubles_details(matchups: List[tuple], players: Dict[str, Player]) -> None:
    """Prints the details for each possible team pairing"""
    for matchup in matchups:
        eval_doubles(
            matchup[0],
            matchup[1],
            matchup[2],
            matchup[3],
            players,
            prob_game=matchup[-1],
            quality=matchup[-2],
        )


if __name__ == "__main__":

    # Parse player names
    # NOTE: either pass in on command line or set in .env file
    _players = sys.argv[1:] or os.environ["PLAYERS"]
    N_PLAYERS = len(_players)
    assert N_PLAYERS > 1, "Needs at least two players"

    singles = not int(os.environ.get("DOUBLES") or 0)

    # Load players/ratings from CSV
    singles_players, doubles_players = build_players()

    # Print the overview table 1st, detail view 2nd
    # NOTE: convoluted way to sort players in order of descending strength...
    #   iterating over single_players first, which IS sorted already
    if singles:
        singles_matchups = print_singles_matchups(
            players=[singles_players[name] for name in _players],
        )
        print_singles_details(matchups=singles_matchups, players=singles_players)
    else:
        doubles_matchups = print_doubles_matchups(
            players=[doubles_players[name] for name in _players],
            delta_mu_threshold=15.0,
            two_rd_threshold=15.0,
        )
        if N_PLAYERS < 7:
            print_doubles_details(matchups=doubles_matchups, players=doubles_players)
