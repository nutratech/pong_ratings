#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 23:34:31 2023

@author: shane
"""
import math
import sys
import time
from datetime import datetime
from typing import Dict, List, Set, Tuple

from tabulate import tabulate

from pong import SINGLES
from pong.core import (
    add_club,
    build_csv_reader,
    cache_ratings_csv_file,
    filter_players,
    get_or_create_player_by_name,
    print_title,
)
from pong.glicko2 import glicko2
from pong.models import Club, Player, SinglesGames


def do_games(player1: Player, player2: Player, games: SinglesGames) -> None:
    """
    Updates ratings for given games & players
    NOTE: player1 wins, player2 loses
    """

    def _update_rating(_player1: Player, _player2: Player) -> None:
        """
        Updates ratings.
        TODO:
            - store date and other meta data in stack
        """
        glicko = glicko2.Glicko2()

        rating1 = _player1.rating_singles
        rating2 = _player2.rating_singles

        # Calculate new ratings
        _new_player1_rating, _new_player2_rating = glicko.rate_1vs1(rating1, rating2)

        # Push to list of ratings
        _player1.ratings[SINGLES].append(_new_player1_rating)
        _player2.ratings[SINGLES].append(_new_player2_rating)

        # Update list of opponent ratings (track e.g. worst defeat & biggest upset)
        # NOTE: these are just the mu values, but the main player stores the rating obj
        _player1.opponent_ratings[SINGLES]["wins"].append(_player2.rating_singles.mu)
        _player2.opponent_ratings[SINGLES]["losses"].append(_player1.rating_singles.mu)

    # pylint: disable=duplicate-code
    # Disallow scores like 2-5
    if games.winner_score() < games.loser_score():
        raise ValueError(
            f"Winner score first in CSV, invalid: "
            f"{games.winner_score()}-{games.loser_score()}"
        )

    # Do the rating updates for won games, then alternate
    for _ in range(games.winner_score() - games.loser_score()):
        _update_rating(player1, player2)

    for _ in range(games.loser_score()):
        _update_rating(player2, player1)
        _update_rating(player1, player2)

    # Push to list of club appearances
    add_club(player1, club=games.location.name, mode=SINGLES)
    add_club(player2, club=games.location.name, mode=SINGLES)


def build_ratings() -> Tuple[List[Player], List[SinglesGames], Set[Club]]:
    """
    Main method which aggregates games, players, clubs.
    And calculates ratings.

    TODO:
     - Support an API level interface?
     - Filter RD > 300/350? Command-line flag / ENV VAR to force anyways?
    """

    # Prepare the CSV inputs (fetch Google Sheet and save to disk)
    reader = build_csv_reader(mode=SINGLES)

    # pylint: disable=duplicate-code
    sets = []
    players: Dict[str, Player] = {}
    clubs = set()

    t_start = time.time()

    # Process the CSV
    for row in reader:
        # Add game to list
        games = SinglesGames(row)
        sets.append(games)

        # Check if players are already tracked, create if not
        _winner_player = get_or_create_player_by_name(players, games.username1)
        _loser_player = get_or_create_player_by_name(players, games.username2)

        # Run the algorithm and update ratings
        do_games(_winner_player, _loser_player, games)

        # pylint: disable=duplicate-code
        # Push to list of club appearances
        clubs.add(games.location)

    n_games = sum(sum(y for y in x.score) for x in sets)

    # Print off rankings
    # TODO: filter inactive or highly uncertain ratings? Group by home club?
    print_title(
        f"Rankings ({n_games} games, {len(players)} players, {len(clubs)} clubs)"
    )
    sorted_players = sorted(
        players.values(), key=lambda x: float(x.rating_singles.mu), reverse=True
    )
    _table = tabulate(
        [
            (
                p.username,
                p.str_rating(mode=SINGLES),
                p.str_win_losses(mode=SINGLES),
                round(max(x.mu for x in p.ratings[SINGLES])),
                p.avg_opponent(mode=SINGLES),
                p.home_club(mode=SINGLES),
            )
            for p in sorted_players
        ],
        headers=["Username", "Glicko 2", "W/L", "Top", "Avg opp", "Club"],
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


def print_singles_matchups(
    players: List[Player],
) -> List[Tuple[str, str, int, int, float, float]]:
    """
    Prints out the fairest possible games, matching up nearly equal opponents for
    interesting play.
    """

    n_players = len(players)
    matchups = []

    rating_engine = glicko2.Glicko2()

    _n_top = 100
    _n_choose_2_players = math.comb(len(players), 2)

    # Evaluate all possible match ups
    # pylint: disable=invalid-name
    for i1 in range(n_players):
        player1 = players[i1]
        # Second player
        for i2 in range(i1 + 1, n_players):
            player2 = players[i2]

            # Compute quality, and add to list
            _delta_rating = round(player1.rating_singles.mu - player2.rating_singles.mu)
            _rd_avg = int(
                round(
                    math.sqrt(
                        (
                            player1.rating_singles.phi**2
                            + player2.rating_singles.phi**2
                        )
                        / 2
                    ),
                    -1,
                )
            )
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

    # Print title and sort
    print_title(
        f"Pair ups [top {min(_n_top, _n_choose_2_players)}, "
        f"{len(players)}C2={_n_choose_2_players} possible]"
    )
    matchups.sort(key=lambda x: float(x[-1]), reverse=True)

    # Verify things
    if len(matchups) != _n_choose_2_players:
        sys.exit(f"Missed some match ups? {len(matchups)} != {_n_choose_2_players}")

    # Print off best matches
    _table = tabulate(
        matchups[:_n_top],
        headers=["Player 1", "Player 2", "Δμ", "RD", "P(w)", "P(l)"],
    )
    print(_table)

    return matchups


def print_progresses(_players: List[Player]) -> None:
    """Prints rating progress graphs"""
    print_title("Rating progress graphs")
    for _player in _players:
        print(
            f"{_player.username} [{_player.str_rating(mode=SINGLES)}], "
            f"peak {round(max(x.mu for x in _player.ratings[SINGLES]))}, "
            f"best win {_player.best_win(mode=SINGLES)}"
        )
        _player.graph_ratings()
        print()


if __name__ == "__main__":
    print("SINGLES")
    print(f"Last updated: {datetime.utcnow()}")

    _sorted_players, _games, _clubs = build_ratings()

    # TODO: make use of _clubs and _games now. Filter uncertain ratings here?
    _sorted_players = filter_players(_sorted_players)
    cache_ratings_csv_file(_sorted_players, mode=SINGLES)

    print_singles_matchups(_sorted_players)

    # Filter players with a highly uncertain rating
    _sorted_players = list(
        filter(lambda x: x.rating_singles.phi * 1.96 < 300, _sorted_players)
    )
    print_progresses(_sorted_players)
