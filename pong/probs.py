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


def match_odds(p: float) -> Dict[int, float]:
    """
    Calculate probability to win a match (best of 3 & best of 5), based on probability
    to win a game.

    :param p: Probability to win one game, between 0.0 - 1.0
    """

    return {
        2: p**2 * (1 + 2 * (1 - p)),
        3: p**3 * (1 + 3 * (1 - p) + 6 * (1 - p) ** 2),
    }


def print_table_common_deuce_odds() -> None:
    """Print a table for common deuce odds"""
    print(os.linesep + "Odds of reaching deuce")
    _series = []
    for _po in [0.5, 0.51, 0.55, 0.6, 0.65, 0.7, 0.8]:
        _do = p_deuce(_po)
        _11go = round(_do[11], 3)
        _21go = round(_do[21], 3)
        _series.append((_po, _11go, _21go))

    _table = tabulate(
        _series,
        headers=["P(p)", "P(20d)", "P(40d)"],
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
        _mo = match_odds(_go)
        _2mo = round(_mo[2], 3)
        _3mo = round(_mo[3], 3)
        _series.append((_go, _2mo, _3mo))

    _table = tabulate(
        _series,
        headers=["P(g)", "P(3m)", "P(5m)"],
    )
    print(_table)


if __name__ == "__main__":
    print_table_common_match_odds()
    print_table_common_game_odds()
    print_table_common_deuce_odds()
