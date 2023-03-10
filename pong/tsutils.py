# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 16:48:05 2023

@author: shane
Helper functions for TrueSkill algo
"""

import itertools
import math
from typing import Tuple

import trueskill  # pylint: disable=import-error
from trueskill import BETA  # pylint: disable=import-error


def win_probability(team1: Tuple, team2: Tuple) -> float:
    """
    Calculate the win probability for team1 vs. team2
    https://trueskill.org/#win-probability
    """
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma**2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    return float(trueskill.global_env().cdf(delta_mu / denom))
