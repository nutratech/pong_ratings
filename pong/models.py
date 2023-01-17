# -*- coding: utf-8 -*-
"""
Created on Sun 08 Jan 2023 11∶26∶34 PM EST

@author: shane
Player model used for singles & doubles ratings, username, wins/losses, etc
"""
from typing import Union

import asciichartpy
import trueskill  # pylint: disable=import-error

from pong.glicko2 import glicko2


class Player:
    """Model for storing username, rating"""

    def __init__(self, username: str):
        self.username = username

        self.rating_singles = glicko2.Glicko2()
        self.stack_ratings_singles = [glicko2.Glicko2().mu]
        self.opponent_rating_wins_singles = []
        self.opponent_rating_losses_singles = []

        self.rating_doubles = trueskill.TrueSkill(draw_probability=0.0)
        self.stack_ratings_doubles = [trueskill.TrueSkill(draw_probability=0.0).mu]
        self.opponent_rating_wins_doubles = []
        self.opponent_rating_losses_doubles = []

    def str_win_losses(self, singles=True) -> str:
        """Returns e.g. 5-2"""

        if singles:
            _wins = len(self.opponent_rating_wins_singles)
            _losses = len(self.opponent_rating_losses_singles)
        else:
            _wins = len(self.opponent_rating_wins_doubles)
            _losses = len(self.opponent_rating_losses_doubles)

        return f"{_wins}-{_losses}"

    @property
    def str_rating_singles(self) -> str:
        """Returns a friendly string for a rating, e.g. 1500 ± 300"""
        _rating = round(self.rating_singles.mu)
        _two_deviations = round(self.rating_singles.phi * 2, -1)  # Round to 10s place
        return f"{_rating} ± {int(_two_deviations)}"

    @property
    def str_rating_doubles(self) -> str:
        """Returns a friendly string for a rating, e.g. 1500 ± 300"""
        _rating = round(self.rating_doubles.mu, 1)
        _two_deviations = round(self.rating_doubles.sigma * 2)
        return f"{_rating} ± {_two_deviations}"

    @property
    def avg_opponent_singles(self) -> int:
        """Returns average opponent in singles"""
        return round(
            (
                sum(self.opponent_rating_wins_singles)
                + sum(self.opponent_rating_losses_singles)
            )
            / (
                len(self.opponent_rating_wins_singles)
                + len(self.opponent_rating_losses_singles)
            )
        )

    @property
    def avg_opponent_doubles(self) -> float:
        """Returns average opponent in doubles"""
        return round(
            (
                sum(self.opponent_rating_wins_doubles)
                + sum(self.opponent_rating_losses_doubles)
            )
            / (
                len(self.opponent_rating_wins_doubles)
                + len(self.opponent_rating_losses_doubles)
            ),
            1,
        )

    @property
    def best_win_singles(self) -> Union[None, int]:
        """Returns best win for singles games"""
        if not self.opponent_rating_wins_singles:
            return None
        return round(max(self.opponent_rating_wins_singles))

    @property
    def best_win_doubles(self) -> Union[None, int]:
        """Returns best win for singles games"""
        if not self.opponent_rating_wins_doubles:
            return None
        return round(max(self.opponent_rating_wins_doubles), 1)

    def __str__(self):
        # NOTE: return this as a tuple, and tabulate it (rather than format as string)?
        return f"{self.username} [{self.str_rating_singles}, {self.str_rating_doubles}]"

    def graph_ratings(self, graph_width_limit=50, graph_height=12) -> None:
        """
        Prints an ASCII graph of rating over past 50 games
        """

        if len(self.stack_ratings_singles) > 1:
            _series = [
                round(x) for x in self.stack_ratings_singles[-graph_width_limit:]
            ]
        # TODO: mutually exclusive for now, we process singles/doubles separately
        elif len(self.stack_ratings_doubles) > 1:
            _series = [
                round(x, 1) for x in self.stack_ratings_doubles[-graph_width_limit:]
            ]
        else:
            _series = []

        if _series:
            _plot = asciichartpy.plot(_series, {"height": graph_height})
            print(_plot)
