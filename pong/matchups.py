#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:19:13 2023

@author: shane
Detailed information about requested match up(s)
"""
import csv
import math
from typing import Dict

import trueskill
from tabulate import tabulate

from pong import CSV_RATINGS_DOUBLES, CSV_RATINGS_SINGLES, DRAW_PROB_DOUBLES
from pong.core import print_subtitle, print_title
from pong.glicko2 import glicko2
from pong.models import Player
from pong.probs import (
    GAME_PERCENT_TO_POINT_PROB,
    p_at_least_k_wins,
    p_deuce,
    p_deuce_win,
    p_match,
)


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
    # TODO: sort by rating, or not here?
    players_dict = _build_players()

    glicko = glicko2.Glicko2()

    # Grab players from usernames
    player1, player2 = players_dict[username1], players_dict[username2]
    rating1, rating2 = player1.rating_singles, player2.rating_singles

    # Calculate misc stats
    _delta_mu = round(rating1.mu - rating2.mu)
    _rd = int(round(math.sqrt((rating1.phi**2 + rating2.phi**2) / 2), -1))

    # Calculate probabilities
    prob_game = glicko.expect_score(
        glicko.scale_down(rating1),
        glicko.scale_down(rating2),
        glicko.reduce_impact(glicko.scale_down(rating2)),
    )

    prob_point = GAME_PERCENT_TO_POINT_PROB[round(prob_game * 100)]

    prob_match = p_match(prob_game)
    prob_win_at_least_1 = p_at_least_k_wins(prob_game)
    prob_deuce_reach = round(p_deuce(prob_point)[11], 2)
    prob_deuce_win = round(p_deuce_win(prob_point), 2)

    # Print off
    print_title(f"{player1.username} & {player2.username} (Δμ={_delta_mu}, RD={_rd})")
    print(player1)
    print(player2)
    print()

    # Game & Deuce probabilities
    # print_subtitle(f"Game & Deuce odds (for {username1})")
    _series = [
        ("Game", round(prob_game, 2)),
        ("Point", round(prob_point, 2)),
        ("Deuce", prob_deuce_reach),
        ("Win deuce", prob_deuce_win),
    ]
    print(tabulate(_series, headers=["", "P(...)"]))
    print()

    # Match probability, and related stats
    print_subtitle("Match odds and rating changes")
    _series = [
        ("Win match", round(prob_match[2], 2), round(prob_match[3], 3)),
        (
            "Win 1+ games",
            round(prob_win_at_least_1[2], 2),
            round(prob_win_at_least_1[3], 3),
        ),
        ("Win all games", round(prob_game**2, 2), round(prob_game**3, 2)),
    ]
    print(tabulate(_series, headers=["P(...)", "3-game", "5-game"]))
    print()

    # New ratings (preview the changes)
    _w_p1, _w_p2 = glicko.rate_1vs1(rating1, rating2)
    _l_p1, _l_p2 = glicko.rate_1vs1(rating2, rating1)
    _series = [
        (player1.username, round(_w_p1.mu - rating1.mu), round(_l_p1.mu - rating1.mu)),
        (player2.username, round(_w_p2.mu - rating2.mu), round(_l_p2.mu - rating2.mu)),
    ]
    _table = tabulate(_series, headers=["", f"{username1} wins", f"{username1} loses"])
    print(_table)
