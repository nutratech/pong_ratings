#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 23:34:31 2023

@author: shane
"""
import math
from datetime import date, datetime
from typing import List

from tabulate import tabulate

from pong.core import (
    build_csv_reader,
    filter_players,
    get_or_create_player_by_name,
    print_title,
)
from pong.glicko2 import glicko2
from pong.models import Player


def do_games(
    player1: Player, player2: Player, _winner_score: int, _loser_score: int
) -> None:
    """
    Updates ratings for given games & players
    NOTE: player1 wins, player2 loses
    """

    def _update_rating(_player1: Player, _player2: Player) -> None:
        """Updates ratings."""

        # Calculate new ratings
        _new_player1_rating, _new_player2_rating = _player1.rating_singles.rate_1vs1(
            _player1.rating_singles, _player2.rating_singles
        )

        # Assign new ratings
        _player1.rating_singles.mu = _new_player1_rating.mu
        _player1.rating_singles.phi = _new_player1_rating.phi
        _player1.rating_singles.sigma = _new_player1_rating.sigma

        _player2.rating_singles.mu = _new_player2_rating.mu
        _player2.rating_singles.phi = _new_player2_rating.phi
        _player2.rating_singles.sigma = _new_player2_rating.sigma

        # Update list of ratings
        _player1.stack_ratings_singles.append(_player1.rating_singles.mu)
        _player2.stack_ratings_singles.append(_player2.rating_singles.mu)

        # Update list of opponent ratings (track e.g. worst defeat & biggest upset)
        _player1.opponent_rating_wins_singles.append(_player2.rating_singles.mu)
        _player2.opponent_rating_losses_singles.append(_player1.rating_singles.mu)

    # Disallow scores like 2-5
    assert _winner_score >= _loser_score, "Winner score first in CSV, e.g. 5-2"

    # Do the rating updates for won games, then alternate
    for _ in range(_winner_score - _loser_score):
        _update_rating(player1, player2)

    for _ in range(_loser_score):
        _update_rating(player2, player1)
        _update_rating(player1, player2)


def build_ratings() -> List[Player]:
    """
    Main method which calculates ratings

    TODO:
     - Support an API level interface?
     - Preview points won / lost
     - Points, server, other details statistics?
    """

    # Prepare the CSV inputs
    reader = build_csv_reader(singles=True)

    players = {}  # Player mapping username -> "class" objects use to store ratings

    # Process the CSV
    for i, row in enumerate(reader):

        # Skip header row
        if i == 0:
            continue

        # Parse fields
        _ = date.fromisoformat(row[0])  # Not used for now
        _winner = row[1].lower()
        _loser = row[2].lower()

        _winner_score = int(row[3].split("-")[0])
        _loser_score = int(row[3].split("-")[1])

        # Check if players are already tracked, create if not
        _winner_player = get_or_create_player_by_name(players, _winner)
        _loser_player = get_or_create_player_by_name(players, _loser)

        # Run the algorithm and update ratings
        do_games(_winner_player, _loser_player, _winner_score, _loser_score)

    # Print off rankings
    # TODO: filter inactive or highly uncertain ratings? Group by home club?
    print_title("Rankings")
    sorted_players = sorted(
        players.values(), key=lambda x: x.rating_singles.mu, reverse=True
    )
    _table = tabulate(
        [
            (
                x.username,
                x.str_rating(singles=True),
                x.str_win_losses(singles=True),
                round(max(x.stack_ratings_singles)),
                x.avg_opponent(singles=True),
            )
            for x in sorted_players
        ],
        headers=["Username", "Glicko 2", "W/L", "Top", "Avg opp"],
    )
    print(_table)

    # Used to build pairings / ideal matches
    return sorted_players


def print_matchups(players: List[Player]) -> None:
    """
    Prints out the fairest possible games, matching up nearly equal opponents for
    interesting play.
    """
    already_matched = set()
    matchups = []
    rating_engine = glicko2.Glicko2()

    # Evaluate all possible match ups
    for player1 in players:
        for player2 in players:

            # Can't play yourself
            if player1 == player2:
                continue

            # Don't double count (p1, p2) AND (p2, p1)... they are the same
            if (player2, player1) in already_matched:
                continue

            # Compute quality, and add to list
            _delta_rating = round(player1.rating_singles.mu - player2.rating_singles.mu)
            _rd_avg = round(
                math.sqrt(
                    (player1.rating_singles.phi**2 + player2.rating_singles.phi**2)
                    / 2
                ),
                -1,
            )
            _rd_avg = int(_rd_avg)
            _win_probability = round(
                rating_engine.expect_score(
                    rating_engine.scale_down(player1.rating_singles),
                    rating_engine.scale_down(player2.rating_singles),
                    rating_engine.reduce_impact(
                        rating_engine.scale_down(player2.rating_singles),
                    ),
                ),
                2,
            )
            _loss_probability = round(
                rating_engine.expect_score(
                    rating_engine.scale_down(player2.rating_singles),
                    rating_engine.scale_down(player1.rating_singles),
                    rating_engine.reduce_impact(
                        rating_engine.scale_down(player1.rating_singles),
                    ),
                ),
                2,
            )

            # Add to list
            matchups.append(
                (
                    player1.username,
                    player2.username,
                    _delta_rating,
                    _rd_avg,
                    _win_probability,
                    _loss_probability,
                )
            )
            already_matched.add((player1, player2))

    # Print off best matches
    _n_top = 100
    _n_choose_2_players = math.comb(len(players), 2)
    print_title(
        f"Matches [top {min(_n_top, _n_choose_2_players)}, "
        f"{len(players)}C2={_n_choose_2_players} possible]"
    )
    matchups.sort(key=lambda x: x[-1], reverse=True)

    _table = tabulate(
        matchups,
        headers=["Player 1", "Player 2", "Δμ", "RD", "P(w)", "P(l)"],
    )
    print(_table)


def print_progresses(_players: List[Player]) -> None:
    """Prints rating progress graphs"""
    print_title("Rating progress graphs")
    for _player in _players:
        print(
            f"{_player.username} [{_player.str_rating()}], "
            f"peak {round(max(_player.stack_ratings_singles))}, "
            f"best win {_player.best_win()}"
        )
        _player.graph_ratings()
        print()


if __name__ == "__main__":
    print("SINGLES")
    print(f"Last updated: {datetime.utcnow()}")

    _sorted_players = filter_players(build_ratings())

    print_matchups(_sorted_players)
    print_progresses(_sorted_players)
