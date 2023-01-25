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


def p_at_least_k_wins(p: float) -> Dict[int, float]:
    """
    Find the probability of winning at least k times out of a best of 3, 5, or 7.
    :param p: Probability to win one game, between 0.0 - 1.0
    """

    def _p_k(k: int) -> float:
        return 1 - (1 - p) ** k

    return {n: _p_k(n) for n in [2, 3, 4]}


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
        _mo = p_at_least_k_wins(_go)
        _2mo = round(_mo[2], 3)
        _3mo = round(_mo[3], 3)
        _4mo = round(_mo[4], 3)
        _series.append((_go, _2mo, _3mo, _4mo))

    _table = tabulate(
        _series,
        headers=["P(g)", "P(3m)", "P(5m)", "P(7m)"],
    )
    print(_table)


GAME_PERCENT_TO_POINT_PROB = [
    0.0,
    0.271999,
    0.296494,
    0.312469,
    0.32469,
    0.33475,
    0.343392,
    0.351027,
    0.357905,
    0.364195,
    0.370011,
    0.375438,
    0.38054,
    0.385367,
    0.389956,
    0.394339,
    0.398541,
    0.402584,
    0.406486,
    0.41026,
    0.413921,
    0.417479,
    0.420943,
    0.424324,
    0.427627,
    0.43086,
    0.434029,
    0.437138,
    0.440194,
    0.4432,
    0.44616,
    0.449078,
    0.451958,
    0.454802,
    0.457614,
    0.460395,
    0.46315,
    0.465879,
    0.468586,
    0.471273,
    0.473941,
    0.476592,
    0.479229,
    0.481853,
    0.484466,
    0.487069,
    0.489665,
    0.492254,
    0.494838,
    0.49742,
    0.5,
    0.50258,
    0.505162,
    0.507746,
    0.510335,
    0.512931,
    0.515534,
    0.518147,
    0.520771,
    0.523408,
    0.526059,
    0.528727,
    0.531414,
    0.534121,
    0.53685,
    0.539605,
    0.542386,
    0.545198,
    0.548042,
    0.550922,
    0.55384,
    0.5568,
    0.559806,
    0.562862,
    0.565971,
    0.56914,
    0.572373,
    0.575676,
    0.579057,
    0.582521,
    0.586079,
    0.58974,
    0.593514,
    0.597416,
    0.601459,
    0.605661,
    0.610044,
    0.614633,
    0.61946,
    0.624562,
    0.629989,
    0.635805,
    0.642095,
    0.648973,
    0.656608,
    0.66525,
    0.67531,
    0.687531,
    0.703506,
    0.728001,
    1.0,
]


if __name__ == "__main__":
    print_table_common_match_odds()
    print_table_common_game_odds()
    print_table_common_deuce_odds()
    print_table_common_match_win_at_least_k_games_odds()
