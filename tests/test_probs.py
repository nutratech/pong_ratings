# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 15:03:24 2023

@author: shane
"""

import pytest

from pong import DRAW_PROB_DOUBLES, probs


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
        # (0.5, 10, DRAW_PROB_DOUBLES),
        # (0.5, 15, 0.2),
        # 0.4 to 0.6 expected results
        # (0.4, 4, 0.84916349599744),
        # (0.5, 8, 0.640716552734375),
        # (0.6, 4, 0.99518057693184),
    ],
)
def test_p_at_least_k_points(p_p: float, k: int, p_k: float):
    """Tests common values for winning >= k points (in a game of 11)"""
    assert p_k == probs.p_at_least_k_points(p_p, k)


@pytest.mark.parametrize(
    "p_g,k,p_k,n",
    [
        (0.0, 0, 1.0, 3),
        (0.0, 1, 0.0, 3),
        # (0.4, 4, 0.84916349599744),
        # (0.5, 8, 0.640716552734375),
        # (0.6, 4, 0.99518057693184),
    ],
)
def test_p_at_least_k_wins(p_g: float, k: int, p_k: float, n: int):
    """Test common values for winning at least k games (match of 3, 5, or 7)"""
    assert p_k == probs.p_at_least_k_wins_in_match(p_g, k)[n]
