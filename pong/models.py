# -*- coding: utf-8 -*-
"""
Created on Sun 08 Jan 2023 11∶26∶34 PM EST

@author: shane
Game model used for players, location, date, outcome, etc.
Player model used for singles & doubles ratings, username, wins/losses, etc.
Club model used for grouping games and players to location names.
"""
import sys
from datetime import date
from typing import Dict, List, Union

import asciichartpy  # pylint: disable=import-error
import trueskill  # pylint: disable=import-error

from pong import DOUBLES, DRAW_PROB_DOUBLES, SINGLES
from pong.glicko2 import glicko2

_PONG_DET = "Pong Det"
CLUB_DICT = {
    "Pong Detroit (Bert's)": _PONG_DET,
    "Pong Detroit (Magee's)": _PONG_DET,
    "Viet Detroit (Grace Parish Warren)": "Viet",
    "MTTA (Sparc Arena Novi)": "MTTA",
    "Norm's": "Norm's",
    "New Way Bar (Ferndale)": "New way",
}

# pylint: disable=too-few-public-methods


class Club:
    """
    Model for storing the club name
    """

    def __init__(self, name: str) -> None:
        self.name = CLUB_DICT[name]

        # Other values populated bi-directionally
        self.games = []
        self.players = []

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


class Games:
    """
    Model for storing date, location, win/loss, opponent, etc.
    Easily queryable, e.g. find max(best_win_opponent_ratings) or avg(opponent_ratings)
    """

    def __init__(self, row: Dict[str, str]) -> None:
        self.date = date.fromisoformat(row["date"])

        self._outcome = row["outcome"]
        self.score = tuple(int(x) for x in self._outcome.split("-"))
        if (self.score[0] < self.score[1]) or len(self.score) != 2:
            print(f"ERROR: failed to parse CSV row: '{self}'")
            print(f"Must have high score first, invalid: {self._outcome}")
            sys.exit()

        self.location = Club(row["location"])

    def winner_score(self) -> int:
        """Gets # games won by player 1 (or team 1)"""
        return self.score[0]

    def loser_score(self) -> int:
        """Gets # games lost by player 2 (or team 2)"""
        return self.score[1]


class SinglesGames(Games):
    """Singles game specifics"""

    def __init__(self, row: Dict[str, str]):
        super().__init__(row=row)

        # TODO: test that these are non-empty values, at least 3 letters long
        #  and check that there are exactly 2 or 4 players
        self.username1 = row["winner"]
        self.username2 = row["loser"]

    def __str__(self) -> str:
        return f"{self.date} {self.username1} vs. {self.username2} {self._outcome}"


class DoublesGames(Games):
    """Doubles game specifics"""

    def __init__(self, row: Dict[str, str]):
        super().__init__(row=row)

        self.username1 = row["winner 1"]
        self.username2 = row["winner 2"]
        self.username3 = row["loser 1"]
        self.username4 = row["loser 2"]

    def __str__(self) -> str:
        return (
            f"{self.date} {self.username1} & {self.username2} vs."
            f"{self.username3} & {self.username4} {self._outcome}"
        )


class Player:
    """
    Model for storing username, rating

    TODO:
        - Include points in scoreboard? Track avg(points) of player1 vs. player2?
        - self.first_game (or self.join_date?)
    """

    def __init__(self, username: str) -> None:
        self.username = username

        # WIP stuff
        # self.singles_games = []
        self.games = {
            "singles": {
                "wins": [],
                "losses": [],
            },
            "doubles": {
                "wins": [],
                "losses": [],
            },
        }
        # NOTE: length of this is one longer than other arrays
        self.ratings = {
            "singles": [glicko2.Glicko2()],
            "doubles": [trueskill.TrueSkill(draw_probability=DRAW_PROB_DOUBLES)],
        }
        self.partner_rating_doubles: List[trueskill.TrueSkill()] = []
        self.opponent_ratings = {
            "singles": {
                "wins": [],
                "losses": [],
            },
            "doubles": {
                "wins": [],
                "losses": [],
            },
        }

        # Used to decide home club
        self.club_appearances: Dict[str, Dict[str, int]] = {
            "singles": {},
            "doubles": {},
        }

    def __str__(self) -> str:
        # NOTE: return this as a tuple, and tabulate it (rather than format as string)?
        return (
            f"{self.username} "
            f"[{self.str_rating(mode=SINGLES)}, {self.str_rating(mode=DOUBLES)}]"
        )

    @property
    def rating_singles(self) -> glicko2.Glicko2:
        """Gets the rating"""
        return self.ratings[SINGLES][-1]

    @property
    def rating_doubles(self) -> trueskill.TrueSkill:
        """Gets the rating"""
        return self.ratings[DOUBLES][-1]

    def home_club(self, mode: str) -> str:
        """Gets the most frequent place of playing"""
        return max(
            self.club_appearances[mode],
            key=self.club_appearances[mode].get,
        )

    def clubs(self):
        """Gets all the clubs someone has appeared at"""
        _clubs = set()
        _clubs.update(self.club_appearances["singles"])
        _clubs.update(self.club_appearances["doubles"])
        return _clubs

    def str_rating(self, mode: str) -> str:
        """Returns a friendly string for a rating, e.g. 1500 ± 300"""

        if mode == SINGLES:
            _rating = round(self.rating_singles.mu)
            _uncertainty = round(self.rating_singles.phi * 1.96, -1)  # Round to 10s
        else:
            _rating = round(self.rating_doubles.mu, 1)
            _uncertainty = round(self.rating_doubles.sigma * 1.96)

        return f"{_rating} ± {int(_uncertainty)}"

    def str_win_losses(self, mode: str) -> str:
        """Returns e.g. 5-2"""

        n_wins = len(self.games[mode]["wins"])
        n_losses = len(self.games[mode]["losses"])

        return f"{n_wins}-{n_losses}"

    def avg_opponent(self, mode: str) -> Union[int, float]:
        """Returns average opponent"""

        _avg_opponent = (
            sum(self.opponent_ratings[mode]["wins"])
            + sum(self.opponent_ratings[mode]["losses"])
        ) / (
            len(self.opponent_ratings[mode]["wins"])
            + len(self.opponent_ratings[mode]["losses"])
        )

        if mode == SINGLES:
            return round(_avg_opponent)
        return round(_avg_opponent, 1)

    def best_win(self, mode: str) -> Union[None, int, float]:
        """Returns best win"""
        _best_win = max(self.opponent_ratings[mode]["wins"])

        if mode == SINGLES:
            return round(_best_win)
        return round(_best_win, 1)

    def graph_ratings(self, graph_width_limit=50, graph_height=12) -> None:
        """
        Prints an ASCII graph of rating over past 50 games
        """

        if len(self.ratings[SINGLES]) > 1:
            _series = [round(x.mu) for x in self.ratings[SINGLES][-graph_width_limit:]]
        # TODO: mutually exclusive for now, we process singles/doubles separately
        elif len(self.ratings[DOUBLES]) > 1:
            _series = [
                round(x.mu, 1) for x in self.ratings[DOUBLES][-graph_width_limit:]
            ]
        else:
            _series = []

        # Don't print the plot for an empty list
        if _series:
            _plot = asciichartpy.plot(_series, {"height": graph_height})
            print(_plot)
