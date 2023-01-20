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
    """
    Model for storing username, rating

    TODO:
        - Include points in scoreboard? Track avg(points) of player1 vs. player2?
    """

    def __init__(self, username: str) -> None:
        self.username = username

        # Track singles related stats
        self.stack_ratings_singles = [glicko2.Glicko2()]
        self.opponent_rating_wins_singles = []
        self.opponent_rating_losses_singles = []

        # Track doubles related stats
        self.stack_ratings_doubles = [trueskill.TrueSkill(draw_probability=0.0)]
        self.partner_rating_doubles = []
        self.opponent_rating_wins_doubles = []
        self.opponent_rating_losses_doubles = []

        # Used to decide home club
        self.club_appearances = {"singles": {}, "doubles": {}}

    def __str__(self) -> str:
        # NOTE: return this as a tuple, and tabulate it (rather than format as string)?
        return (
            f"{self.username} [{self.str_rating()}, {self.str_rating(singles=False)}]"
        )

    @property
    def rating_singles(self) -> glicko2.Glicko2:
        """Gets the rating"""
        return self.stack_ratings_singles[-1]

    @property
    def rating_doubles(self) -> trueskill.TrueSkill:
        """Gets the rating"""
        return self.stack_ratings_doubles[-1]

    def home_club(self, singles=True) -> str:
        """Gets the most frequent place of playing"""

        def _abbrev_club(_club: str) -> str:
            _pong_det = "Pong Det"
            return {
                "Pong Detroit": _pong_det,
                "Bert's": _pong_det,
                "McGee's": _pong_det,
                "Viet Detroit": "Viet",
                "Norm's": "Norm's",
            }[_club]

        if singles:
            _club = max(
                self.club_appearances["singles"],
                key=self.club_appearances["singles"].get,
            )
        else:
            _club = max(
                self.club_appearances["singles"],
                key=self.club_appearances["doubles"].get,
            )
        return _abbrev_club(_club)

    def str_rating(self, singles=True) -> str:
        """Returns a friendly string for a rating, e.g. 1500 ± 300"""
        if singles:
            _rating = round(self.rating_singles.mu)
            _uncertainty = round(self.rating_singles.phi * 1.96, -1)  # Round to 10s
        else:
            _rating = round(self.rating_doubles.mu, 1)
            _uncertainty = round(self.rating_doubles.sigma * 1.96)

        return f"{_rating} ± {int(_uncertainty)}"

    def str_win_losses(self, singles=True) -> str:
        """Returns e.g. 5-2"""

        if singles:
            _wins = len(self.opponent_rating_wins_singles)
            _losses = len(self.opponent_rating_losses_singles)
        else:
            _wins = len(self.opponent_rating_wins_doubles)
            _losses = len(self.opponent_rating_losses_doubles)

        return f"{_wins}-{_losses}"

    def avg_opponent(self, singles=True) -> int:
        """Returns average opponent"""
        if singles:
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

    def best_win(self, singles=True) -> Union[None, int]:
        """Returns best win"""
        if singles:
            if self.opponent_rating_wins_singles:
                return round(max(self.opponent_rating_wins_singles))
        else:
            if self.opponent_rating_wins_doubles:
                return round(max(self.opponent_rating_wins_doubles), 1)
        return None

    def graph_ratings(self, graph_width_limit=50, graph_height=12) -> None:
        """
        Prints an ASCII graph of rating over past 50 games
        """

        if len(self.stack_ratings_singles) > 1:
            _series = [
                round(x.mu) for x in self.stack_ratings_singles[-graph_width_limit:]
            ]
        # TODO: mutually exclusive for now, we process singles/doubles separately
        elif len(self.stack_ratings_doubles) > 1:
            _series = [
                round(x.mu, 1) for x in self.stack_ratings_doubles[-graph_width_limit:]
            ]
        else:
            _series = []

        # Don't print the plot for an empty list
        if _series:
            _plot = asciichartpy.plot(_series, {"height": graph_height})
            print(_plot)
