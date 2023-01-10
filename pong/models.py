# -*- coding: utf-8 -*-
"""
Created on Sun 08 Jan 2023 11∶26∶34 PM EST

@author: shane
"""
from pong.glicko2 import glicko2

DEFAULT_RATING = 1500


class Player:
    """Model for storing username, rating"""

    def __init__(self, username: str):
        self.username = username

        self.rating_singles = glicko2.Glicko2()

    @property
    def str_rating_singles(self):
        """Returns a friendly string for a rating, e.g. 1500 ± 300"""
        _rating = round(self.rating_singles.mu)
        _two_deviations = round(self.rating_singles.phi * 2)
        return f"{_rating} ± {_two_deviations}"

    def __str__(self):
        # NOTE: return this as a tuple, and tabulate it (rather than format as string)?
        return f"{self.username} ({self.str_rating_singles})"
