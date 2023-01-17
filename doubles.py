#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri 13 Jan 2023 01∶14∶59 PM EST

@author: shane
https://trueskill.org/
"""
import math
import time
from datetime import date, datetime
from typing import List

import trueskill  # pylint: disable=import-error
from tabulate import tabulate

from pong.core import (
    build_csv_reader,
    filter_players,
    get_or_create_player_by_name,
    print_title,
)
from pong.models import Player
from pong.tsutils import win_probability


def do_games(
    player1: Player,
    player2: Player,
    player3: Player,
    player4: Player,
    _winners_score: int,
    _losers_score: int,
) -> None:
    """
    Updates ratings.
    NOTE: team1 = wins, team2 = loses
          team1 = (player1, player2), team2 = (player3, player4)
    """

    def _update_rating(
        _player1: Player, _player2: Player, _player3: Player, _player4: Player
    ) -> None:
        """Updates ratings."""

        # Calculate new ratings
        _new_team1_ratings, _new_team2_ratings = trueskill.rate(
            [
                (_player1.rating_doubles, _player2.rating_doubles),
                (_player3.rating_doubles, _player4.rating_doubles),
            ]
        )

        # Assign new ratings
        _player1.rating_doubles = _new_team1_ratings[0]
        _player2.rating_doubles = _new_team1_ratings[1]

        _player3.rating_doubles = _new_team2_ratings[0]
        _player4.rating_doubles = _new_team2_ratings[1]

        # Update list of ratings
        for _player in [_player1, _player2, _player3, _player4]:
            _player.stack_ratings_doubles.append(_player.rating_doubles.mu)

        # Update list of opponent ratings (track e.g. worst defeat & biggest upset)
        for _player in [_player1, _player2]:
            _player.opponent_rating_wins_doubles.append(
                (_player3.rating_doubles.mu + _player4.rating_doubles.mu) / 2
            )
        for _player in [_player3, _player4]:
            _player.opponent_rating_losses_doubles.append(
                (_player1.rating_doubles.mu + _player2.rating_doubles.mu) / 2
            )

    # Disallow scores like 2-5
    assert _winners_score >= _losers_score, "Winner score first in CSV, e.g. 5-2"

    # Do the rating updates for won games, then alternate
    for _ in range(_winners_score - _losers_score):
        _update_rating(player1, player2, player3, player4)

    for _ in range(_losers_score):
        _update_rating(player4, player3, player2, player1)
        _update_rating(player1, player2, player3, player4)


def build_ratings() -> List[Player]:
    """
    Main method which calculates ratings

    TODO:
     - Support TrueSkill and multiplayer (doubles games) ratings
     - Support an API level interface?
    """

    # Prepare the CSV inputs
    reader = build_csv_reader(singles=False)

    players = {}  # Player mapping username -> "class" objects use to store ratings

    # Process the CSV
    for i, row in enumerate(reader):  # pylint: disable=duplicate-code

        # Skip header row
        if i == 0:
            continue

        # Parse fields
        _ = date.fromisoformat(row[0])  # Not used for now
        _winner1 = row[1].lower()
        _winner2 = row[2].lower()

        _loser1 = row[3].lower()
        _loser2 = row[4].lower()

        _winners_score = int(row[5].split("-")[0])
        _losers_score = int(row[5].split("-")[1])

        # Check if players are already tracked, create if not
        _winner_player1 = get_or_create_player_by_name(players, _winner1)
        _winner_player2 = get_or_create_player_by_name(players, _winner2)
        _loser_player1 = get_or_create_player_by_name(players, _loser1)
        _loser_player2 = get_or_create_player_by_name(players, _loser2)

        # Run the algorithm and update ratings
        do_games(
            _winner_player1,
            _winner_player2,
            _loser_player1,
            _loser_player2,
            _winners_score,
            _losers_score,
        )

    # Print off rankings
    # TODO: filter inactive or highly uncertain ratings?
    print_title("Doubles rankings")
    sorted_players = sorted(
        players.values(), key=lambda x: x.rating_doubles.mu, reverse=True
    )
    _table = tabulate(
        [
            (
                x.username,
                x.str_rating_doubles,
                x.str_win_losses(singles=False),
                round(max(x.stack_ratings_doubles), 1),
                x.avg_opponent_doubles,
            )
            for x in sorted_players
        ],
        headers=["Username", "TrueSkill", "W/L", "Top", "Avg opp"],
    )
    print(_table)

    # Used to build pairings / ideal matches
    return sorted_players


def print_matchups(players: List[Player]) -> None:
    """
    Prints out the fairest possible games, matching up nearly equal opponents for
    interesting play.
    """

    t_start = time.time()
    already_matched = set()
    matchups = []

    # Evaluate all possible match ups
    for player1 in players:
        for player2 in players:
            for player3 in players:
                for player4 in players:

                    # Can't play yourself
                    if player1 in {player2, player3, player4}:
                        continue
                    if player2 in {player1, player3, player4}:
                        continue
                    if player3 in {player1, player2, player4}:
                        continue
                    if player4 in {player1, player2, player3}:
                        continue

                    # Don't double count (t1, t2) AND (t2, t1)... the same teams
                    team1 = "-".join(
                        x.username
                        for x in sorted([player1, player2], key=lambda x: x.username)
                    )
                    team2 = "-".join(
                        x.username
                        for x in sorted([player3, player4], key=lambda x: x.username)
                    )
                    pair1, pair2 = (team1, team2), (team2, team1)
                    if pair1 in already_matched or pair2 in already_matched:
                        continue

                    # Compute quality, and add to list
                    _delta_rating = (
                        player1.rating_doubles.mu
                        + player2.rating_doubles.mu
                        - player3.rating_doubles.mu
                        - player4.rating_doubles.mu
                    ) / 2
                    _delta_rating = round(_delta_rating, 1)
                    _rd_avg = round(
                        math.sqrt(
                            sum(
                                x.rating_doubles.sigma**2
                                for x in [player1, player2, player3, player4]
                            )
                            / 4
                        )
                    )

                    _quality_of_match = round(
                        trueskill.quality(
                            [
                                (player1.rating_doubles, player2.rating_doubles),
                                (player3.rating_doubles, player4.rating_doubles),
                            ]
                        ),
                        2,
                    )
                    _win_probability = round(
                        win_probability(
                            (player1.rating_doubles, player2.rating_doubles),
                            (player3.rating_doubles, player4.rating_doubles),
                        ),
                        2,
                    )

                    # Add to list
                    matchups.append(
                        (
                            player1.username,
                            player2.username,
                            player3.username,
                            player4.username,
                            _delta_rating,
                            _rd_avg,
                            _quality_of_match,
                            _win_probability,
                        )
                    )
                    already_matched.add((team1, team2))

    # Print off best matches
    _n_top = 100
    _n_choose_2_teams = math.comb(len(players), 2) * math.comb(len(players) - 2, 2) // 2
    print_title(
        f"Doubles matches [top {min(_n_top, _n_choose_2_teams)}, "
        f"{len(players)}C2*{len(players) - 2}C2/2={_n_choose_2_teams} possible]"
    )
    matchups.sort(key=lambda x: x[-2], reverse=True)

    _table = tabulate(
        matchups[:_n_top],
        headers=["Team 1", "Team 1", "Team 2", "Team 2", "Δμ", "rd", "Q", "P(w)"],
    )
    print(_table)
    t_delta = time.time() - t_start
    print()
    print(
        f"Calculated {len(matchups)} matches in {round(t_delta, 5) * 1000}ms "
        f"({round(_n_choose_2_teams / t_delta)}/s)"
    )


def print_progresses(_players: List[Player]) -> None:
    """Prints rating progress graphs"""
    print_title("Rating progress graphs")
    for _player in _players:
        print(
            f"{_player.username} [{_player.str_rating_doubles}], "
            f"peak {round(max(_player.stack_ratings_doubles), 1)}, "
            f"best win {_player.best_win_doubles}"
        )
        _player.graph_ratings()
        print()


if __name__ == "__main__":
    print("DOUBLES")
    print(f"Last updated: {datetime.utcnow()}")

    _sorted_players = filter_players(build_ratings())

    print_matchups(_sorted_players)
    print_progresses(_sorted_players)
