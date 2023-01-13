# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 16:48:05 2023

@author: shane
Helper functions for TrueSkill algo
"""

import itertools
import math

import trueskill
from trueskill import BETA


def win_probability(team1, team2):
    """Calculate the win probability for team1 vs. team2"""
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma**2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    ts = trueskill.global_env()
    return ts.cdf(delta_mu / denom)
