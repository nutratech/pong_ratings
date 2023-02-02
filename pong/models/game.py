# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 15:50:20 2023

@author: shane
Game model, used to represent game date, location, outcome, participants, ratings, etc.
"""
from datetime import date

from pong.models.player import Player


class Game:
    """
    Model for storing date, location, win/loss, opponent, etc.
    Easily queryable, e.g. find max(best_win_opponent_ratings) or avg(opponent_ratings)
    """

    def __init__(
        self,
        date_str: str,
        player1: Player,
        player2: Player,
        winners_score: int,
        losers_score: int,
    ) -> None:

        self.date = date.fromisoformat(date_str)

        self.player1 = player1
        self.player2 = player2

        self.winners_score = winners_score
        self.losers_score = losers_score


class SinglesGame(Game):
    """Singles game specifics"""

    def __init__(
        self,
        date_str: str,
        player1: Player,
        player2: Player,
        winners_score: int,
        losers_score: int,
    ):
        super().__init__(
            date_str=date_str,
            player1=player1,
            player2=player2,
            winners_score=winners_score,
            losers_score=losers_score,
        )


class DoublesGame:
    """Doubles game specifics"""

    def __init__(
        self,
        date_str: str,
        player1: Player,
        player2: Player,
        player3: Player,
        player4: Player,
        winners_score: int,
        losers_score: int,
    ):
        super().__init__(
            date_str=date_str,
            player1=player1,
            player2=player2,
            winners_score=winners_score,
            losers_score=losers_score,
        )
        self.player3 = player3
        self.player4 = player4
