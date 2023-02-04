#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri 13 Jan 2023 01∶14∶59 PM EST

@author: shane
https://trueskill.org/
"""
import math
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Set, Tuple

import trueskill  # pylint: disable=import-error
from tabulate import tabulate

from pong import DOUBLES
from pong.core import (
    add_club,
    build_csv_reader,
    cache_ratings_csv_file,
    filter_players,
    get_or_create_player_by_name,
    print_title,
)
from pong.models import Club, DoublesGames, Player
from pong.tsutils import win_probability


def do_games(
    player1: Player,
    player2: Player,
    player3: Player,
    player4: Player,
    games: DoublesGames,
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
        _player1.ratings[DOUBLES].append(_new_team1_ratings[0])
        _player2.ratings[DOUBLES].append(_new_team1_ratings[1])
        _player1.partner_rating_doubles.append(_player2.rating_doubles)
        _player2.partner_rating_doubles.append(_player1.rating_doubles)

        _player3.ratings[DOUBLES].append(_new_team2_ratings[0])
        _player4.ratings[DOUBLES].append(_new_team2_ratings[1])
        _player3.partner_rating_doubles.append(_player4.rating_doubles)
        _player4.partner_rating_doubles.append(_player3.rating_doubles)

        # Update list of opponent ratings (track e.g. worst defeat & biggest upset)
        for _player in [_player1, _player2]:
            _player.opponent_ratings[DOUBLES]["wins"].append(
                (_player3.rating_doubles.mu + _player4.rating_doubles.mu) / 2
            )
        for _player in [_player3, _player4]:
            _player.opponent_ratings[DOUBLES]["losses"].append(
                (_player1.rating_doubles.mu + _player2.rating_doubles.mu) / 2
            )

    # Disallow scores like 2-5
    if games.winner_score() < games.loser_score():
        raise ValueError(
            f"Winner score first in CSV, invalid: "
            f"{games.winner_score()}-{games.loser_score()}"
        )

    # Do the rating updates for won games, then alternate
    for _ in range(games.winner_score() - games.loser_score()):
        _update_rating(player1, player2, player3, player4)

    for _ in range(games.loser_score()):
        _update_rating(player4, player3, player2, player1)
        _update_rating(player1, player2, player3, player4)

    # Push to list of club locations
    add_club(player1, club=games.location.name, mode=DOUBLES)
    add_club(player2, club=games.location.name, mode=DOUBLES)
    add_club(player3, club=games.location.name, mode=DOUBLES)
    add_club(player4, club=games.location.name, mode=DOUBLES)


def build_ratings() -> Tuple[List[Player], List[DoublesGames], Set[Club]]:
    """
    Main method which calculates ratings

    TODO:
     - Support TrueSkill and multiplayer (doubles games) ratings
     - Support an API level interface?
    """

    # Prepare the CSV inputs (fetch Google Sheet and save to disk)
    reader = build_csv_reader(mode=DOUBLES)

    # pylint: disable=duplicate-code
    sets = []
    players: Dict[str, Player] = {}
    clubs = set()

    t_start = time.time()

    # Process the CSV
    for row in reader:
        # Add game to list
        games = DoublesGames(row)
        sets.append(games)

        # Check if players are already tracked, create if not
        _winner_player1 = get_or_create_player_by_name(players, games.username1)
        _winner_player2 = get_or_create_player_by_name(players, games.username2)
        _loser_player1 = get_or_create_player_by_name(players, games.username3)
        _loser_player2 = get_or_create_player_by_name(players, games.username4)

        # Run the algorithm and update ratings
        do_games(
            _winner_player1, _winner_player2, _loser_player1, _loser_player2, games
        )

        # Push to list of club locations
        clubs.add(games.location)

    n_games = sum(sum(y for y in x.score) for x in sets)

    # Print off rankings
    # TODO: filter inactive or highly uncertain ratings?
    print_title(
        f"Rankings ({n_games} games, {len(players)} players, {len(clubs)} clubs)"
    )
    sorted_players = sorted(
        players.values(),
        key=lambda x: x.rating_doubles.mu,  # type: ignore
        reverse=True,
    )
    _table = tabulate(
        [
            (
                p.username,
                p.str_rating(mode=DOUBLES),
                p.str_win_losses(mode=DOUBLES),
                round(max(x.mu for x in p.ratings[DOUBLES]), 1),
                p.avg_opponent(mode=DOUBLES),
                round(
                    sum(x.mu for x in p.partner_rating_doubles)
                    / len(p.partner_rating_doubles),
                    1,
                ),
                p.home_club(mode=DOUBLES),
            )
            for p in sorted_players
        ],
        headers=["Username", "TrueSkill", "W/L", "Top", "Avg opp", "T mate", "Club"],
    )
    # pylint: disable=duplicate-code
    print(_table)

    # Show time elapsed
    t_delta = time.time() - t_start
    print()
    print(
        f"Analyzed {len(sets)} CSV lines in {round(1000 * t_delta, 1)} ms "
        f"({round(len(sets) / t_delta)}/s)"
    )

    # Used to build pairings / ideal matches
    return sorted_players, sets, clubs


def print_doubles_matchups(
    players: List[Player],
    delta_mu_threshold: float = 3.0,
    two_rd_threshold: float = 9.5,
) -> List[Tuple[str, str, str, str, float, int, float, float]]:
    """
    Prints out the fairest possible games, matching up nearly equal opponents for
    interesting play.
    """

    t_start = time.time()
    n_players = len(players)
    matchups = []
    n_skipped_matchups = 0

    _n_top = 100
    # TODO: resolve ValueError with len(players) < 2, allow to just do the pair ups for
    #   that one person with everyone else, or that club, or something specific
    _n_choose_2_teams = math.comb(len(players), 2) * math.comb(len(players) - 2, 2) // 2
    _avg_cmp_per_second = 30000

    # Evaluate all possible match ups
    # pylint: disable=invalid-name
    print(
        os.linesep + f"Calculating {_n_choose_2_teams} match ups, "
        f"should take ~{round(_n_choose_2_teams / _avg_cmp_per_second, 2)}s"
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
                    if i4 in {i3, i2}:
                        continue
                    player4 = players[i4]

                    # Compute rating difference and average RD
                    _delta_rating = float(
                        round(
                            (
                                player1.rating_doubles.mu
                                + player2.rating_doubles.mu
                                - player3.rating_doubles.mu
                                - player4.rating_doubles.mu
                            )
                            / 2,
                            1,
                        )
                    )

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
                    if (
                        _delta_rating > delta_mu_threshold
                        or _2_rd_avg > two_rd_threshold
                    ):
                        n_skipped_matchups += 1
                        continue

                    # Compute quality metrics, and add to list
                    # NOTE: relatively slow to calculate
                    _quality_of_match = float(
                        round(
                            trueskill.quality(
                                [
                                    (player1.rating_doubles, player2.rating_doubles),
                                    (player3.rating_doubles, player4.rating_doubles),
                                ]
                            ),
                            2,
                        )
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
    matchups.sort(key=lambda x: x[-2], reverse=True)

    # Verify things
    if len(matchups) + n_skipped_matchups != _n_choose_2_teams:
        sys.exit(
            f"Missed some match ups? "
            f"{len(matchups)} + {n_skipped_matchups} != {_n_choose_2_teams}"
        )

    # Print off best matches
    _table = tabulate(
        matchups[:_n_top],
        headers=["Team 1", "Team 1", "Team 2", "Team 2", "Δμ", "2σ", "Q", "P(w)"],
    )
    print(_table)

    # Show time elapsed
    t_delta = time.time() - t_start
    print()
    print(
        f"Assessed {_n_choose_2_teams} pairings in {round(t_delta * 1000, 1)}ms "
        f"({round(_n_choose_2_teams / t_delta)}/s), "
        f"skipped {n_skipped_matchups}"
    )

    return matchups


def print_progresses(_players: List[Player]) -> None:
    """Prints rating progress graphs"""
    print_title("Rating progress graphs")
    for _player in _players:
        print(
            f"{_player.username} [{_player.str_rating(mode=DOUBLES)}], "
            f"peak {round(max(x.mu for x in _player.ratings[DOUBLES]), 1)}, "
            f"best win {_player.best_win(mode=DOUBLES)}"
        )
        _player.graph_ratings()
        print()


if __name__ == "__main__":
    print("DOUBLES")
    print(f"Last updated: {datetime.utcnow()}")

    _sorted_players, _games, _clubs = build_ratings()

    # TODO: make use of _clubs and _games now. Filter uncertain ratings here?
    _sorted_players = filter_players(_sorted_players)
    cache_ratings_csv_file(_sorted_players, mode=DOUBLES)

    # TODO: filter, or match based on club, or create greedy pairing algorithm
    #  this has O(n^4) complexity and won't scale
    print_doubles_matchups(_sorted_players)
    print_progresses(_sorted_players)
