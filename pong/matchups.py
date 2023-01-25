#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:19:13 2023

@author: shane
Detailed information about requested match up(s)
"""
import csv
from typing import Dict

import trueskill

from pong import CSV_RATINGS_DOUBLES, CSV_RATINGS_SINGLES, DRAW_PROB_DOUBLES
from pong.glicko2 import glicko2
from pong.models import Player


def _build_players() -> Dict[str, Player]:
    """Builds the players from the updated ratings_*.csv file"""

    players: Dict[str, Player] = {}

    # Singles
    with open(CSV_RATINGS_SINGLES, encoding="utf-8") as _f:
        csv_reader = csv.DictReader(_f)

        for row in csv_reader:
            player = Player(username=row["username"])

            player.stack_ratings_singles[0] = glicko2.Glicko2(
                mu=float(row["mu"]),
                phi=float(row["phi"]),
                sigma=float(row["sigma"]),
            )

            players[player.username] = player

    # Doubles
    with open(CSV_RATINGS_DOUBLES, encoding="utf-8") as _f:
        csv_reader = csv.DictReader(_f)

        for row in csv_reader:
            username = row["username"]

            # Check if player was read up in SINGLES CSV
            if username in players:
                players[username].stack_ratings_doubles[0] = trueskill.TrueSkill(
                    mu=float(row["mu"]),
                    sigma=float(row["sigma"]),
                    draw_probability=DRAW_PROB_DOUBLES,
                )

            # Otherwise, create a new player for doubles
            else:
                player = Player(username=row["username"])
                player.stack_ratings_singles[0] = trueskill.TrueSkill(
                    mu=float(row["mu"]),
                    sigma=float(row["sigma"]),
                )
                players[player.username] = player

    return players


def eval_singles(username1: str, username2: str) -> None:
    """Print out stats for player1 vs. player2"""
    players = _build_players()

    # Grab players from usernames
    player1 = players[username1]
    player2 = players[username2]

    print(player1)
    print(player2)


if __name__ == "__main__":
    eval_singles("thomas", "benji")
