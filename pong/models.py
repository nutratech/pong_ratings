# -*- coding: utf-8 -*-
"""
Created on Sun 08 Jan 2023 11∶26∶34 PM EST

@author: shane
Player model used for singles & doubles ratings, username, wins/losses, etc
"""
import asciichartpy
import trueskill  # pylint: disable=import-error

from pong.glicko2 import glicko2


class Player:
    """Model for storing username, rating"""

    def __init__(self, username: str):
        self.username = username

        self.rating_singles = glicko2.Glicko2()
        self.stack_ratings_singles = [glicko2.Glicko2().mu]
        self.wins_singles = 0
        self.losses_singles = 0

        self.rating_doubles = trueskill.TrueSkill(draw_probability=0.0)
        self.stack_ratings_doubles = [trueskill.TrueSkill(draw_probability=0.0).mu]
        self.wins_doubles = 0
        self.losses_doubles = 0

    @property
    def str_rating_singles(self) -> str:
        """Returns a friendly string for a rating, e.g. 1500 ± 300"""
        _rating = round(self.rating_singles.mu)
        _two_deviations = round(self.rating_singles.phi * 2)
        return f"{_rating} ± {_two_deviations}"

    @property
    def str_rating_doubles(self) -> str:
        """Returns a friendly string for a rating, e.g. 1500 ± 300"""
        _rating = round(self.rating_doubles.mu, 1)
        _two_deviations = round(self.rating_doubles.sigma * 2, 1)
        return f"{_rating} ± {_two_deviations}"

    def __str__(self):
        # NOTE: return this as a tuple, and tabulate it (rather than format as string)?
        return f"{self.username} [{self.str_rating_singles}, {self.str_rating_doubles}]"

    def graph_ratings(self, graph_width_limit=50, graph_height=10) -> None:
        """
        Prints an ASCII graph of rating over past 50 games
        """

        if len(self.stack_ratings_singles) > 1:
            _series = self.stack_ratings_singles[-graph_width_limit:]
        # NOTE: mutually exclusive for now, we process singles/doubles separately
        elif len(self.stack_ratings_doubles) > 1:
            _series = self.stack_ratings_doubles[-graph_width_limit:]
        else:
            _series = []

        if _series:
            _plot = asciichartpy.plot(_series, {"height": graph_height})
            print(_plot)
