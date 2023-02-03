# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 15:03:24 2023

@author: shane
"""
from typing import Dict

import pytest

from pong import probs

# pylint: disable=invalid-name


@pytest.mark.parametrize(
    "input_dict",
    [
        # Trivial cases
        {"p_g": 0.0, "n": 2, "p_m": 0.0},
        {"p_g": 1.0, "n": 2, "p_m": 1.0},
        # Other test cases
        {"p_g": 0.3, "n": 2, "p_m": 0.216},
        {"p_g": 0.3, "n": 3, "p_m": 0.16307999999999995},
        {"p_g": 0.3, "n": 4, "p_m": 0.12603599999999998},
    ],
)
def test_p_match(input_dict: Dict) -> None:
    """Tests the P_match(P_game) function"""
    p_g, n, p_m = input_dict["p_g"], input_dict["n"], input_dict["p_m"]
    assert probs.p_match(p_g, n) == p_m


@pytest.mark.parametrize(
    "p_p,k,p_k",
    [
        # All or nothing cases
        (0.0, 0, 1.0),
        (0.0, 1, 0.0),
        (1.0, 10, 1.0),
        # Near deuce, deuce, and post-deuce
        # (0.5, 8, 0.7),
        # (0.5, 9, 0.6),
        (0.5, 10, probs.p_deuce(0.5) + probs.p_game_straight(0.5)),
        # (0.5, 15, 0.2),
        # 0.4 to 0.6 expected results
        # (0.4, 4, 0.84916349599744),
        # (0.5, 8, 0.640716552734375),
        # (0.6, 4, 0.99518057693184),
    ],
)
def test_p_at_least_k_points(p_p: float, k: int, p_k: float) -> None:
    """Tests common values for winning >= k points (in a game of 11)"""
    assert probs.p_at_least_k_points(p_p, k) == p_k


@pytest.mark.parametrize(
    "n,p_g,k,p_k",
    [
        # n=3 => m=5 (best of 5, first to win 3)
        # Trivial cases
        (3, 0.0, 0, 1.0),
        (3, 0.0, 1, 0.0),
    ],
)
def test_p_at_least_k_wins(n: int, p_g: float, k: int, p_k: float) -> None:
    """Test common values for winning at least k games (match of 3, 5, or 7)"""
    assert probs.p_at_least_k_wins_in_match(p_g, n, k) == p_k


if __name__ == "__main__":
    pytest.main()
