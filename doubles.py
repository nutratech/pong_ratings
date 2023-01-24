#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri 13 Jan 2023 01∶14∶59 PM EST

@author: shane
https://trueskill.org/
"""
import math
import os
import time
from datetime import date, datetime
from typing import List

import trueskill  # pylint: disable=import-error
from tabulate import tabulate

from pong.core import (
    build_csv_reader,
    cache_ratings_csv_file,
    filter_players,
    get_or_create_player_by_name,
    print_title,
    add_club,
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

        # Push to list of ratings
        _player1.stack_ratings_doubles.append(_new_team1_ratings[0])
        _player2.stack_ratings_doubles.append(_new_team1_ratings[1])
        _player1.partner_rating_doubles.append(_player2.rating_doubles)
        _player2.partner_rating_doubles.append(_player1.rating_doubles)

        _player3.stack_ratings_doubles.append(_new_team2_ratings[0])
        _player4.stack_ratings_doubles.append(_new_team2_ratings[1])
        _player3.partner_rating_doubles.append(_player4.rating_doubles)
        _player4.partner_rating_doubles.append(_player3.rating_doubles)

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
    if _winners_score < _losers_score:
        raise ValueError(
            f"Winner score first in CSV, invalid: {_winners_score}-{_losers_score}"
        )

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

        _winners_score = int(row[3].split("-")[0])
        _losers_score = int(row[3].split("-")[1])

        _loser1 = row[4].lower()
        _loser2 = row[5].lower()

        _location = row[6]  # Club name or location of game

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

        # Push to list of club locations
        for player in [
            _winner_player1,
            _winner_player2,
            _loser_player1,
            _loser_player2,
        ]:
            add_club(player, _location, singles=False)

    # Print off rankings
    # TODO: filter inactive or highly uncertain ratings?
    print_title("Rankings")
    sorted_players = sorted(
        players.values(), key=lambda x: x.rating_doubles.mu, reverse=True
    )
    _table = tabulate(
        [
            (
                p.username,
                p.str_rating(singles=False),
                p.str_win_losses(singles=False),
                round(max(x.mu for x in p.stack_ratings_doubles), 1),
                p.avg_opponent(singles=False),
                round(
                    sum(x.mu for x in p.partner_rating_doubles)
                    / len(p.partner_rating_doubles),
                    1,
                ),
                p.home_club(singles=False),
            )
            for p in sorted_players
        ],
        headers=["Username", "TrueSkill", "W/L", "Top", "Avg opp", "T mate", "Club"],
    )
    print(_table)

    # Used to build pairings / ideal matches
    return sorted_players


def print_matchups(players: List[Player]) -> None:
    """
    Prints out the fairest possible games, matching up nearly equal opponents for
    interesting play.
    """

    # players = [Player(f"id_{x}") for x in range(20)]
    # import numpy
    # for player in players:
    #     player.rating_doubles.mu = numpy.random.normal(25, 5, 1)[0]
    #     player.rating_doubles.sigma = numpy.random.normal(25/3, 3, 1)[0]

    #     print(player.rating_doubles)

    t_start = time.time()
    n_players = len(players)
    matchups = []
    n_skipped_matchups = 0

    _n_top = 100
    _n_choose_2_teams = math.comb(len(players), 2) * math.comb(len(players) - 2, 2) // 2
    _avg_cmps_per_second = 30000

    # Evaluate all possible match ups
    # pylint: disable=invalid-name
    print(
        os.linesep + f"Calculating {_n_choose_2_teams} match ups, "
        f"should take ~{round(_n_choose_2_teams / _avg_cmps_per_second, 2)}s"
    )
    for i1 in range(n_players):
        player1 = players[i1]
        for i2 in range(i1 + 1, n_players):
            player2 = players[i2]

            # Second team
            for i3 in range(i1 + 1, n_players):
                # Can't play yourself
                if i3 == i2:
                    continue
                player3 = players[i3]

                for i4 in range(i3 + 1, n_players):
                    # Can't play yourself
                    if i4 in (i2, i1):
                        continue
                    player4 = players[i4]

                    # Compute rating difference and average RD
                    _delta_rating = (
                        player1.rating_doubles.mu
                        + player2.rating_doubles.mu
                        - player3.rating_doubles.mu
                        - player4.rating_doubles.mu
                    ) / 2
                    _delta_rating = round(_delta_rating, 1)

                    _2_rd_avg = round(
                        1.96
                        * math.sqrt(
                            sum(
                                x.rating_doubles.sigma**2
                                for x in [player1, player2, player3, player4]
                            )
                            / 4
                        )
                    )
                    # Short list only match ups with small delta mu and small sigma
                    if _delta_rating > 3 or _2_rd_avg > 9.5:
                        n_skipped_matchups += 1
                        continue

                    # Compute quality metrics, and add to list
                    # NOTE: commented out because it is relatively slow to calculate
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
                            _2_rd_avg,
                            _quality_of_match,
                            _win_probability,
                        )
                    )

    # Print title and sort
    print_title(
        f"Pair ups [top {min(_n_top, _n_choose_2_teams)}, "
        f"({len(players)}C2*{len(players) - 2}C2)/2={_n_choose_2_teams} possible]"
    )
    matchups.sort(key=lambda x: math.fabs(0.5 - x[-2]), reverse=True)

    # Verify things
    # assert (
    #     len(matchups) + n_skipped_matchups == _n_choose_2_teams
    # ), "Missed some match ups?"

    # Print off best matches
    _table = tabulate(
        matchups[:_n_top],
        headers=["Team 1", "Team 1", "Team 2", "Team 2", "Δμ", "2σ", "Q", "P(w)"],
    )
    print(_table)
    t_delta = time.time() - t_start
    print()
    print(
        f"Assessed {_n_choose_2_teams} pairings in {round(t_delta * 1000, 1)}ms "
        f"({round(_n_choose_2_teams / t_delta)}/s), "
        f"skipped {n_skipped_matchups}"
    )


def print_progresses(_players: List[Player]) -> None:
    """Prints rating progress graphs"""
    print_title("Rating progress graphs")
    for _player in _players:
        print(
            f"{_player.username} [{_player.str_rating(singles=False)}], "
            f"peak {round(max(x.mu for x in _player.stack_ratings_doubles), 1)}, "
            f"best win {_player.best_win(singles=False)}"
        )
        _player.graph_ratings()
        print()


if __name__ == "__main__":
    print("DOUBLES")
    print(f"Last updated: {datetime.utcnow()}")

    _sorted_players = filter_players(build_ratings())
    cache_ratings_csv_file(_sorted_players, singles=False)

    # _sorted_players = list(
    #     filter(lambda x: x.rating_doubles.sigma * 1.96 < 9, _sorted_players)
    # )
    print_matchups(_sorted_players)
    # print_progresses(_sorted_players)
