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
from pong.core import print_title
from pong.glicko2 import glicko2
from pong.models import Player
from pong.probs import p_at_least_k_wins, p_deuce, p_deuce_win, p_match


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
            # print(row)

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
                player.stack_ratings_doubles[0] = trueskill.TrueSkill(
                    mu=float(row["mu"]),
                    sigma=float(row["sigma"]),
                )
                players[player.username] = player

    return players


def eval_singles(username1: str, username2: str) -> None:
    """Print out stats for player1 vs. player2"""
    players_dict = _build_players()

    singles_engine = glicko2.Glicko2()

    # Grab players from usernames
    player1 = players_dict[username1]
    player2 = players_dict[username2]

    # Calculate probabilities
    prob_game = singles_engine.expect_score(
        singles_engine.scale_down(player1.rating_singles),
        singles_engine.scale_down(player2.rating_singles),
        singles_engine.reduce_impact(
            singles_engine.scale_down(
                player2.rating_singles,
            )
        ),
    )

    prob_match = p_match(prob_game)
    prob_win_at_least_1 = p_at_least_k_wins(prob_game)
    prob_deuce_reach = p_deuce(prob_game)
    prob_deuce_win = p_deuce_win(prob_game)

    # Print off
    print_title(f"{player1.username} & {player2.username}")
    print(player1)
    print(player2)
    print()
    print(f"Game prob:         {round(prob_game, 4)}")
    print()
    print(f"3 game match prob: {round(prob_match[2], 4)}")
    print(f"5 game match prob: {round(prob_match[3], 4)}")
    print()
    print(f"Prob to win 1+ games (3 game match): {round(prob_win_at_least_1[2], 4)}")
    print(f"Prob to win 1+ games (5 game match): {round(prob_win_at_least_1[3], 4)}")
    print()
    print(f"Prob to win 2 straight: {round(prob_game**2, 4)}")
    print(f"Prob to win 3 straight: {round(prob_game**3, 4)}")
    print()
    print(f"Prob to reach deuce: {round(prob_deuce_reach[11], 4)}")
    print(f"Prob to win deuce:   {round(prob_deuce_win, 4)}")
    # print(
    #     tabulate.tabulate(
    #         [(p.username, p.rating_singles, p.rating_doubles) for p in players],
    #         headers=['username', 'singles', 'doubles']
    #     )
    # )
