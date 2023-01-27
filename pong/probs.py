# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 14:24:28 2023

@author: shane
Probability tools used for side statistics.
"""
import math
import os
from typing import Dict

from tabulate import tabulate

# pylint: disable=invalid-name


def p_deuce(p: float) -> Dict[int, float]:
    """
    Get probability of reaching 10-10 score, based on probability to win a point.
    :param p: Probability of winning an individual point
    """
    return {
        n: p ** (n - 1) * (1 - p) ** (n - 1) * math.comb(2 * (n - 1), n - 1)
        for n in [11, 21]
    }


def p_deuce_win(p: float) -> float:
    """
    Get probability of winning at deuce (two points in a row).
    :param p: Probability of winning an individual point
    """
    return p**2 / (1 - 2 * p * (1 - p))


def p_game(p: float) -> Dict[int, float]:
    """
    Probability of winning a game, based on probability to win a point.
    :param p: Probability of winning an individual point
    """

    def _p_n(n: int) -> float:
        _sum = sum(
            p**n * (1 - p) ** k * (math.comb(n - 1 + k, k)) for k in range(0, n - 1)
        )
        _sum += p_deuce(p)[n] * p_deuce_win(p)
        return round(_sum, 3)

    return {n: _p_n(n) for n in [11, 21]}


def p_at_least_k_points(p: float, k: int) -> float:
    """
    Find the probability of winning at least k points in a game to 11.
    :param p: Probability of winning an individual point
    :param k: Points to win (k < 10)
    """

    def p_n(n: int) -> float:
        """Probability to win exactly n points, n < 10"""
        assert n < 10, "Can't calculate n > 9 pts"
        return math.comb(11 + n, n) * p**n * (1 - p) ** 11

    return 1 - sum(p_n(i) for i in range(k))


def p_at_least_k_wins_in_match(p: float, k: int) -> Dict[int, float]:
    """
    Find the probability of winning at least k times out of a best of 3, 5, or 7.
    :param p: Probability to win one game, between 0.0 - 1.0
    :param k: Number of games to win
    # TODO: p_at_least_k_wins_out_of_n_games()
    """
    assert k < 5, "Only matches up to 7 games are supported, e.g. k=4"

    def _p_n_k(n: int, _k=1) -> float:
        """
        :param n: Win n games to win the match, e.g. 2 or 3
        :param _k: Win at least k games, e.g. win at least 1 game against a good player
        """
        return 1 - (1 - p) ** n

    return {n: _p_n_k(n) for n in [2, 3, 4]}


def p_match(p: float) -> Dict[int, float]:
    """
    Calculate probability to win a match (best of 3 & best of 5), based on probability
    to win a game.

    :param p: Probability to win one game, between 0.0 - 1.0
    """

    return {
        2: p**2 * (1 + 2 * (1 - p)),
        3: p**3 * (1 + 3 * (1 - p) + 6 * (1 - p) ** 2),
        4: p**4 * (1 + 4 * (1 - p) + 10 * (1 - p) ** 2 + 20 * (1 - p) ** 3),
    }


def print_table_common_deuce_odds() -> None:
    """Print a table for common deuce odds"""
    print(os.linesep + "Odds of reaching deuce")
    _series = []
    for _po in [0.5, 0.51, 0.55, 0.6, 0.65, 0.7, 0.8]:
        _do = p_deuce(_po)
        _20do = round(_do[11], 3)
        _40do = round(_do[21], 3)
        _pwd = round(_po**2 / (1 - 2 * _po * (1 - _po)), 3)
        _series.append((_po, _20do, _40do, _pwd))

    _table = tabulate(
        _series,
        headers=["P(p)", "P(20d)", "P(40d)", "P(wd)"],
    )
    print(_table)


def print_table_common_game_odds() -> None:
    """Print a table for common game odds"""
    print(os.linesep + "Game odds")
    _series = []
    for _po in [0.5, 0.51, 0.55, 0.6, 0.65, 0.7, 0.8]:
        _go = p_game(_po)
        _11go = _go[11]
        _21go = _go[21]
        _series.append((_po, _11go, _21go))

    _table = tabulate(
        _series,
        headers=["P(p)", "P(11g)", "P(21g)"],
    )
    print(_table)


def print_table_common_match_odds() -> None:
    """Print a table for common match odds"""
    print(os.linesep + "Match odds")
    _series = []
    for _go in [0.05, 0.1, 0.2, 0.3, 0.4, 0.45, 0.5]:
        _mo = p_match(_go)
        _2mo = round(_mo[2], 3)
        _3mo = round(_mo[3], 3)
        _4mo = round(_mo[4], 3)
        _series.append((_go, _2mo, _3mo, _4mo))

    _table = tabulate(
        _series,
        headers=["P(g)", "P(3m)", "P(5m)", "P(7m)"],
    )
    print(_table)


def print_table_common_match_win_at_least_k_games_odds() -> None:
    """Print a table for common chances to win, e.g. at least 1 or 2 games in a match"""
    print(os.linesep + "Chances to win at least 1 game")
    _series = []
    for _go in [0.05, 0.1, 0.2, 0.3, 0.4, 0.45, 0.5]:
        # TOD: hard coded k=1, for now that's all the equation supports
        _mo = p_at_least_k_wins_in_match(_go, 1)
        _2mo = round(_mo[2], 3)
        _3mo = round(_mo[3], 3)
        _4mo = round(_mo[4], 3)
        _series.append((_go, _2mo, _3mo, _4mo))

    _table = tabulate(
        _series,
        headers=["P(g)", "P(3m)", "P(5m)", "P(7m)"],
    )
    print(_table)


if __name__ == "__main__":
    print_table_common_match_odds()
    print_table_common_game_odds()
    print_table_common_deuce_odds()
    print_table_common_match_win_at_least_k_games_odds()
