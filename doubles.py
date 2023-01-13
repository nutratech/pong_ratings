#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri 13 Jan 2023 01∶14∶59 PM EST

@author: shane
"""
from datetime import date
from typing import List

import trueskill  # pylint: disable=import-error
from tabulate import tabulate

from pong.core import (
    DOUBLES_URL,
    build_csv_reader,
    get_or_create_player_by_name,
    print_title,
)
from pong.models import Player


def do_games(
    player1: Player,
    player2: Player,
    player3: Player,
    player4: Player,
    _winners_score: int,
    _losers_score: int,
):
    """
    Updates ratings.
    NOTE: team1 = wins, team2 = loses
          team1 = (player1, player2), team2 = (player3, player4)
    """

    def _update_rating(
        _player1: Player, _player2: Player, _player3: Player, _player4: Player
    ):
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

    # Do the rating updates for won games, then lost games
    #  e.g. 2-1... so 2 wins for the winner, AND then 1 loss for him/her
    # NOTE: do losses come before wins? It influences the ratings slightly
    for _ in range(_losers_score):
        player4.wins_doubles += 1
        player3.wins_doubles += 1
        player2.losses_doubles += 1
        player1.losses_doubles += 1
        _update_rating(player4, player3, player2, player1)

    for _ in range(_winners_score):
        player1.wins_doubles += 1
        player2.wins_doubles += 1
        player3.losses_doubles += 1
        player4.losses_doubles += 1
        _update_rating(player1, player2, player3, player4)


def build_ratings():
    """
    Main method which calculates ratings

    TODO:
     - Support TrueSkill and multiplayer (doubles games) ratings
     - Support an API level interface?
    """

    # Prepare the CSV inputs
    reader = build_csv_reader(DOUBLES_URL)

    players = {}  # Player mapping username -> "class" objects use to store ratings

    # Process the CSV
    for i, row in enumerate(reader):  # pylint: disable=duplicate-code

        # Skip header row
        if i == 0:
            continue

        # Parse fields
        _ = date.fromisoformat(row[0])  # Not used for now
        _winner1 = row[1]
        _winner2 = row[2]

        _loser1 = row[3]
        _loser2 = row[4]

        _winners_score = int(row[5].split("-")[0])
        _losers_score = int(row[5].split("-")[1])

        # Check if players are already tracked, create if not
        _winner_player1 = get_or_create_player_by_name(players, _winner1)
        _winner_player2 = get_or_create_player_by_name(players, _winner2)
        _loser_player1 = get_or_create_player_by_name(players, _loser1)
        _loser_player2 = get_or_create_player_by_name(players, _loser2)

        # Run the algorithm and update ratings
        # NOTE: we're assuming these are singles games only (for now)
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
            (x.username, x.str_rating_doubles, f"{x.wins_doubles}-{x.losses_doubles}")
            for x in sorted_players
        ],
        headers=["Username", "TrueSkill", "Record"],
    )
    print(_table)

    # Used to build pairings / ideal matches
    return sorted_players


def print_matchups(players: List[Player]):
    """
    Prints out the fairest possible games, matching up nearly equal opponents for
    interesting play.
    """
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
                    quality_of_match = round(
                        trueskill.quality(
                            [
                                (player1.rating_doubles, player2.rating_doubles),
                                (player3.rating_doubles, player4.rating_doubles),
                            ]
                        ),
                        3,
                    )
                    matchups.append(
                        (
                            player1.username,
                            player2.username,
                            player3.username,
                            player4.username,
                            quality_of_match,
                        )
                    )
                    already_matched.add((team1, team2))

    # Print off best matches
    _n_top = 15
    _n_choose_2_teams = len(matchups)
    print_title(
        f"Doubles matches [top {min(_n_top, _n_choose_2_teams)}, "
        f"P({len(players)},2,2)={_n_choose_2_teams} possible]"
    )
    matchups.sort(key=lambda x: x[4], reverse=True)

    _table = tabulate(
        matchups[:_n_top], headers=["Team 1", "Team 1", "Team 2", "Team 2", "Quality"]
    )
    print(_table)


if __name__ == "__main__":
    # NOTE: Also need to support DOUBLES rankings & matches (not just singles)
    print("DOUBLES")
    print(f"Last updated: {date.today()}")
    _sorted_players = build_ratings()
    print_matchups(_sorted_players)