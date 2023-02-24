# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:19:13 2023

@author: shane
Detailed information about requested match up(s)
"""
import csv
import math
from typing import Dict, Set, Tuple

import trueskill
from tabulate import tabulate

from pong import CSV_RATINGS_FILE_PATHS, DOUBLES, SINGLES
from pong.consts import GAME_PERCENT_TO_POINT_PROB
from pong.glicko2 import glicko2
from pong.models import Player
from pong.probs import (
    n_fair_handicap_points,
    p_at_least_k_wins_in_match,
    p_at_least_k_wins_out_of_n_games,
    p_deuce,
    p_deuce_win,
    p_match,
)
from pong.utils import print_subtitle, print_title


def add_player_to_club(player: Player, club: str, clubs: Dict[str, Set[str]]) -> None:
    """Create a club (if it doesn't exist) and add a player to its list"""
    if club in clubs:
        clubs[club].add(player.username)
    else:
        clubs[club] = set(player.username)


def build_players() -> Tuple[Dict[str, Player], Dict[str, Player]]:
    """Builds the players from the updated ratings_*.csv file"""

    singles_players: Dict[str, Player] = {}
    doubles_players: Dict[str, Player] = {}
    clubs: Dict[str, Set[str]] = {}

    # Singles
    with open(CSV_RATINGS_FILE_PATHS[SINGLES], encoding="utf-8") as _f:
        csv_reader = csv.DictReader(_f)

        for row in csv_reader:
            player = Player(username=row["username"])

            # Set rating
            player.ratings[SINGLES][0] = glicko2.Glicko2(
                mu=float(row["mu"]),
                phi=float(row["phi"]),
                sigma=float(row["sigma"]),
            )

            # Populate player's clubs
            for club in row["clubs"].split("|"):
                add_player_to_club(player, club, clubs)

            # Add to list
            singles_players[player.username] = player

    # Doubles
    with open(CSV_RATINGS_FILE_PATHS[DOUBLES], encoding="utf-8") as _f:
        csv_reader = csv.DictReader(_f)

        for row in csv_reader:
            player = Player(username=row["username"])

            # Set rating
            player.ratings[DOUBLES][0] = trueskill.TrueSkill(
                mu=float(row["mu"]),
                sigma=float(row["sigma"]),
            )

            # Populate player's clubs
            for club in row["clubs"].split("|"):
                add_player_to_club(player, club, clubs)

            # Add to list
            doubles_players[player.username] = player

    return singles_players, doubles_players


def _inverse_probs(
    prob_game: float,
) -> Tuple[Dict[str, float], Dict[str, Dict[int, float]]]:
    """Returns common match / point / game metrics to both singles & doubles"""

    prob_point = GAME_PERCENT_TO_POINT_PROB[round(prob_game * 10000)]

    prob_match = {n: p_match(prob_game, n) for n in [2, 3, 4]}
    prob_win_at_least_1 = {
        n: p_at_least_k_wins_in_match(prob_game, n, k=1) for n in [2, 3, 4]
    }
    prob_deuce_reach = round(p_deuce(prob_point), 2)
    prob_deuce_win = round(p_deuce_win(prob_point), 2)
    prob_win_6_out_of_6 = round(prob_game**6, 3)

    return (
        {
            "prob_point": prob_point,
            "prob_deuce_reach": prob_deuce_reach,
            "prob_deuce_win": prob_deuce_win,
            "prob_win_6_out_of_6": prob_win_6_out_of_6,
        },
        {
            "prob_match": prob_match,
            "prob_win_at_least_1": prob_win_at_least_1,
        },
    )


def detailed_match_ups_singles(
    username1: str, username2: str, players: Dict[str, Player]
) -> None:
    """
    Print out stats for player1 vs. player2
    """

    # Only use singles ratings for this
    glicko = glicko2.Glicko2()

    # Alias players and ratings
    player1, player2 = players[username1], players[username2]
    rating1, rating2 = player1.rating_singles, player2.rating_singles

    # Calculate misc stats
    _delta_mu = round(rating1.mu - rating2.mu)
    _rd = int(round(math.sqrt((rating1.phi**2 + rating2.phi**2) / 2), -1))

    # Calculate probabilities
    prob_p1_game = glicko.expect_score(
        glicko.scale_down(rating1),
        glicko.scale_down(rating2),
        glicko.reduce_impact(glicko.scale_down(rating2)),
    )
    prob_p2_game = glicko.expect_score(
        glicko.scale_down(rating2),
        glicko.scale_down(rating1),
        glicko.reduce_impact(glicko.scale_down(rating1)),
    )
    prob_game = (prob_p1_game + (1 - prob_p2_game)) / 2

    inverse_probs_pts, inverse_probs_match = _inverse_probs(prob_game)

    prob_point = float(inverse_probs_pts["prob_point"])
    prob_match: Dict[int, float] = inverse_probs_match["prob_match"]
    prob_win_at_least_1: Dict[int, float] = inverse_probs_match["prob_win_at_least_1"]
    prob_win_6_out_of_6 = float(inverse_probs_pts["prob_win_6_out_of_6"])

    prob_deuce_reach = inverse_probs_pts["prob_deuce_reach"]
    prob_deuce_win = inverse_probs_pts["prob_deuce_win"]

    # Calculate other statistics
    fair_handicap = [
        (f"0-{n}", round(p, 3)) for n, p in n_fair_handicap_points(prob_point)
    ]
    _n_out_of = 10
    prob_win_k_out_of_n = [
        (k, round(p_at_least_k_wins_out_of_n_games(prob_game, n=_n_out_of, k=k), 3))
        for k in range(_n_out_of + 1)
    ]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Print off the details
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    print_title(f"{username1} & {username2} (Δμ={_delta_mu}, RD={_rd})")

    # Game & Deuce probabilities
    _series_gdp = [
        ("Game", round(prob_game, 2)),
        ("Point", round(prob_point, 3)),
        ("Deuce", prob_deuce_reach),
        ("Win deuce", prob_deuce_win),
        ("Win 6/6", prob_win_6_out_of_6),
    ]
    print(tabulate(_series_gdp, headers=["x", "P(x)"]))
    print()

    # Other stats
    print_subtitle(f"Point handicaps & Win n+ out of {_n_out_of}")
    print(tabulate(fair_handicap, headers=["H-cap", "P(w)"]))
    print()
    print(tabulate(prob_win_k_out_of_n, headers=["n", "P(n+)"]))
    print()

    # Match probability, and related stats
    print_subtitle("Match odds and rating changes")
    _series_mp = [
        ("Win match", round(prob_match[2], 2), round(prob_match[3], 3)),
        (
            "Win 1+ games",
            round(prob_win_at_least_1[2], 2),
            round(prob_win_at_least_1[3], 3),
        ),
        ("Win all games", round(prob_game**2, 2), round(prob_game**3, 2)),
    ]
    print(tabulate(_series_mp, headers=["P(...)", "3-game", "5-game"]))
    print()

    # New ratings (preview the changes)
    _w_p1, _w_p2 = glicko.rate_1vs1(rating1, rating2)
    _l_p2, _l_p1 = glicko.rate_1vs1(rating2, rating1)
    _series_pr = [
        (
            player1.username,
            player1.str_rating(mode=SINGLES),
            round(_w_p1.mu - rating1.mu),
            round(_l_p1.mu - rating1.mu),
            round(_w_p1.phi + _l_p1.phi - 2 * rating1.phi, 1),
        ),
        (
            player2.username,
            player2.str_rating(mode=SINGLES),
            round(_w_p2.mu - rating2.mu),
            round(_l_p2.mu - rating2.mu),
            round(_w_p2.phi + _l_p2.phi - 2 * rating2.phi, 1),
        ),
    ]
    _table = tabulate(
        _series_pr,
        headers=["Player", "μ", f"{username1} wins", f"{username1} loses", "avg(ΔΦ)"],
    )
    print(_table)


# pylint: disable=too-many-arguments
def detailed_match_ups_doubles(
    username1: str,
    username2: str,
    username3: str,
    username4: str,
    players: Dict[str, Player],
    prob_game: float,
    quality: float,
) -> None:
    """
    Print out stats for (player1, player2) vs. (player3, player4)
    """

    # FIXME: draw_probability=DRAW_PROB_DOUBLES
    # Only use doubles ratings for this
    tse = trueskill.TrueSkill()

    # Alias players and ratings
    player1, player2 = players[username1], players[username2]
    player3, player4 = players[username3], players[username4]
    rating1, rating2 = player1.rating_doubles, player2.rating_doubles
    rating3, rating4 = player3.rating_doubles, player4.rating_doubles

    # Calculate misc stats
    _delta_mu = round((rating1.mu + rating2.mu - rating3.mu - rating3.mu) / 2, 1)
    _2rd = round(
        1.96
        * math.sqrt(
            sum(r.sigma**2 for r in [rating1, rating2, rating3, rating4]) / 4
        ),
        1,
    )

    # Calculate probabilities
    inverse_probs_pts, inverse_probs_match = _inverse_probs(prob_game)

    prob_point = float(inverse_probs_pts["prob_point"])
    prob_match: Dict[int, float] = inverse_probs_match["prob_match"]
    prob_win_at_least_1: Dict[int, float] = inverse_probs_match["prob_win_at_least_1"]
    prob_win_6_out_of_6 = float(inverse_probs_pts["prob_win_6_out_of_6"])

    prob_deuce_reach = inverse_probs_pts["prob_deuce_reach"]
    prob_deuce_win = inverse_probs_pts["prob_deuce_win"]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Print off the details
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    print_title(
        f"{username1} & {username2} vs. {username3} & {username4} "
        f"(Δμ={_delta_mu}, 2σ={_2rd})"
    )

    # Quality
    print(f"Q = {quality}")
    print()

    # Game & Deuce probabilities
    _series_gdp = [
        ("Game", round(prob_game, 2)),
        ("Point", round(prob_point, 3)),
        ("Deuce", prob_deuce_reach),
        ("Win deuce", prob_deuce_win),
        ("Win 6/6", prob_win_6_out_of_6),
    ]
    print(tabulate(_series_gdp, headers=["x", "P(x)"]))
    print()

    # Match probability, and related stats
    print_subtitle("Match odds and rating changes")
    _series_mp = [
        ("Win match", round(prob_match[2], 2), round(prob_match[3], 3)),
        (
            "Win 1+ games",
            round(prob_win_at_least_1[2], 2),
            round(prob_win_at_least_1[3], 3),
        ),
        ("Win all games", round(prob_game**2, 2), round(prob_game**3, 2)),
    ]
    print(tabulate(_series_mp, headers=["P(...)", "3-game", "5-game"]))
    print()

    # New ratings (preview the changes)
    _w_t1, _w_t2 = tse.rate([(rating1, rating2), (rating3, rating4)])
    _l_t2, _l_t1 = tse.rate([(rating3, rating4), (rating1, rating2)])
    # noinspection DuplicatedCode
    _series_pr = [
        (
            player1.username,
            player1.str_rating(mode=DOUBLES),
            round(_w_t1[0].mu - rating1.mu, 1),
            round(_l_t1[0].mu - rating1.mu, 1),
            round(_w_t1[0].sigma + _l_t1[0].sigma - 2 * rating1.sigma, 1),
        ),
        (
            player2.username,
            player2.str_rating(mode=DOUBLES),
            round(_w_t1[1].mu - rating2.mu, 1),
            round(_l_t1[1].mu - rating2.mu, 1),
            round(_w_t1[1].sigma + _l_t1[1].sigma - 2 * rating2.sigma, 1),
        ),
        (
            player3.username,
            player3.str_rating(mode=DOUBLES),
            round(_w_t2[0].mu - rating3.mu, 1),
            round(_l_t2[0].mu - rating3.mu, 1),
            round(_w_t2[0].sigma + _l_t2[0].sigma - 2 * rating3.sigma, 1),
        ),
        (
            player4.username,
            player4.str_rating(mode=DOUBLES),
            round(_w_t2[1].mu - rating4.mu, 1),
            round(_l_t2[1].mu - rating4.mu, 1),
            round(_w_t2[1].sigma + _l_t2[1].sigma - 2 * rating4.sigma, 1),
        ),
    ]
    _table = tabulate(
        _series_pr,
        headers=["Player", "μ", "T1 wins", "T2 wins", "avg(Δσ)"],
    )
    print(_table)
