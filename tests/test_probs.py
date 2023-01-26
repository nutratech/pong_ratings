# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 15:03:24 2023

@author: shane
"""

import pytest

from pong import probs


@pytest.mark.parametrize(
    "p_p,k,p_k",
    [
        (0.0, 0, 1.0),
        (0.0, 1, 0.0),
        (1.0, 10, 1.0),
        (0.5, 10, 0.3363761901855469),
        (0.4, 4, 0.84916349599744),
        (0.5, 8, 0.640716552734375),
        (0.6, 4, 0.99518057693184),
    ],
)
def test_p_at_least_k_points(p_p: float, k: int, p_k: float):
    """Tests common values for winning >= k points (in a game of 11)"""
    assert p_k == probs.p_at_least_k_points(p_p, k)


@pytest.mark.parametrize(
    "p_g,k,p_k",
    [
        (0.0, 0, 1.0),
        (0.0, 1, 0.0),
        (0.4, 4, 0.84916349599744),
        (0.5, 8, 0.640716552734375),
        (0.6, 4, 0.99518057693184),
    ],
)
def test_p_at_least_k_wins(p_g: float, k: int, p_k: float):
    """Test common values for winning at least k games (match of 3, 5, or 7)"""
