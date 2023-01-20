# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 14:24:28 2023

@author: shane
Probability tools used for side statistics.
"""
from typing import Dict

from tabulate import tabulate


# pylint: disable=invalid-name


def match_odds(p: float) -> Dict[int, float]:
    """
    Calculate probability to win a match (best of 3 & best of 5), based on probability
    to win a game.

    :param p: Probability to win one game, between 0.0 - 1.0
    """

    return {
        2: p**2 * (3 - 2 * p),
        3: p**3 * (1 + 3 * (1 - p) + 6 * (1 - p) ** 2),
    }


def match_odds_common_print_table() -> None:
    """Print a table for common match odds"""
    _series = []
    for _go in [0.05, 0.1, 0.2, 0.3, 0.4, 0.45]:
        _mo = match_odds(_go)
        _2mo = round(_mo[2], 4)
        _3mo = round(_mo[3], 4)
        _series.append((_go, _2mo, _3mo))

    _table = tabulate(
        _series,
        headers=["P(g)", "P(3m)", "P(5m)"],
    )
    print(_table)


if __name__ == "__main__":
    match_odds_common_print_table()
