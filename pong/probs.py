# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 14:24:28 2023

@author: shane
Probability tools used for side statistics.
"""
import math
import os

from tabulate import tabulate

# pylint: disable=invalid-name


def p_game_straight(p: float, n=11) -> float:
    """
    Probability of winning a game (without going to deuce, e.g. 11-9 or 11-0)
    :param p: Probability of winning an individual point
    :param n: Points to win game (e.g. 11 or 21)
    """
    # Sums this expression up from k=0 to 9 (if n=11)
    return sum(math.comb(n - 1 + k, k) * p**n * (1 - p) ** k for k in range(0, n - 1))


def p_deuce(p: float, n=11) -> float:
    """
    Get probability of reaching 10-10 score, based on probability to win a point.
    :param p: Probability of winning an individual point
    :param n: Points to win game (e.g. 11 or 21)
    """
    return p ** (n - 1) * (1 - p) ** (n - 1) * math.comb(2 * (n - 1), n - 1)


def p_deuce_win(p: float) -> float:
    """
    Get probability of winning at deuce (two points in a row).
    :param p: Probability of winning an individual point
    """
    return p**2 / (1 - 2 * p * (1 - p))


def p_game(p: float, n=11) -> float:
    """
    Probability of winning a game, based on probability to win a point.
    :param p: Probability of winning an individual point
    :param n: Points to win game (e.g. 11 or 21)
    """
    return p_game_straight(p, n) + p_deuce(p, n) * p_deuce_win(p)


def p_at_least_k_points(p: float, k: int) -> float:
    """
    Find the probability of winning at least k points in a game to 11.
    :param p: Probability of winning an individual point
    :param k: Goal to score # of points (k < 11), e.g. 1, 4, or 6
    """

    assert k < 11, "Can't calculate k > 10 pts"

    # Probabilities based on game of 11 points (not 21)
    prob_lose_with_k_points = math.comb(11 + k, k) * p**k * (1 - p) ** 11
    prob_deuce = p_deuce(p)
    prob_win_straight = p_game_straight(p)

    # "Trivial case with k=0 has P=1.0"
    if k == 0:
        return 1.0

    # k=10  =>  P(deuce) + P(straight win)
    if k == 10:
        return prob_deuce + prob_win_straight

    # k<10  =>  P(straight loss with k points) + P(deuce) + P(win)
    return prob_lose_with_k_points + prob_deuce + prob_win_straight


def p_at_least_k_wins_in_match(p: float, n: int, k: int) -> float:
    """
    Find the probability of winning at least k times out of a best of 3, 5, or 7.
    :param p: Probability to win one game, between 0.0 - 1.0
    :param n: Number of games to win the match
    :param k: Desired number to win (e.g. win at least 1 in a best of 5)
    # TODO: p_at_least_k_wins_out_of_n_games()
    """

    def _prob_lose_match_win_i_games(i: int) -> float:
        return math.comb(n + i, i) * (1 - p) ** n * p**i

    assert n > 0, "Can't have a best of zero"
    assert 0 <= k < n, f"Desired wins k must be between 0 and {n}"

    # m = 2 * n - 1  # e.g. n=3, m=5

    # Probabilities based on the match
    prob_match = p_match(p, n)

    # "Trivial case k=0 has P=1.0 for all match sizes"
    if k == 0:
        return 1.0

    # P(win) + Sum [P(lose & win i games), for i in range(k)]
    return prob_match + sum(_prob_lose_match_win_i_games(i) for i in range(k))

    # def _p_n_k(n: int, _k=1) -> float:
    #     """
    #     :param n: Win n games to win the match, e.g. 2 or 3
    #     :param _k: Win at least k games, e.g. win at least 1 game against a good player
    #     """
    #     if _k > n:
    #         return -1.0
    #     return 1 - (1 - p) ** n
    #
    # return _p_n_k(n)


def p_match(p: float, n: int) -> float:
    """
    Calculate probability to win a match (best of 3 & best of 5), based on probability
    to win a game.

    :param p: Probability to win one game, between 0.0 - 1.0
    :param n: First to win n games, e.g. win 3 games => 5 game match

    First few examples, best of 3, 5, and 7:
        2: p**2 * (1 + 2 * (1 - p)),
        3: p**3 * (1 + 3 * (1 - p) + 6 * (1 - p) ** 2),
        4: p**4 * (1 + 4 * (1 - p) + 10 * (1 - p) ** 2 + 20 * (1 - p) ** 3),
    """
    return p**n * sum(math.comb(n - 1 + k, k) * (1 - p) ** k for k in range(n))


def print_table_common_deuce_odds() -> None:
    """Print a table for common deuce odds"""
    print(os.linesep + "Odds of reaching deuce")
    _series = []
    for _po in [0.5, 0.51, 0.55, 0.6, 0.65, 0.7, 0.8]:
        _20do = round(p_deuce(_po, n=11), 3)
        _40do = round(p_deuce(_po, n=21), 3)
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
        _11go = round(p_game(_po, n=11), 3)
        _21go = round(p_game(_po, n=21), 3)
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
        _2mo = round(p_match(_go, n=2), 3)
        _3mo = round(p_match(_go, n=3), 3)
        _4mo = round(p_match(_go, n=4), 3)
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
        # TODO: hard coded k=1, for now that's all the equation supports
        _2mo = round(p_at_least_k_wins_in_match(_go, n=2, k=1), 3)
        _3mo = round(p_at_least_k_wins_in_match(_go, n=3, k=1), 3)
        _4mo = round(p_at_least_k_wins_in_match(_go, n=4, k=1), 3)
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
