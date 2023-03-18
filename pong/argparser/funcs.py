#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:26:28 2023

@author: shane
"""
import argparse
from typing import Any, Dict, List, Set, Tuple

from pong.core import func_match_ups, func_rank, process_csv
from pong.models import Club, Game, Player
from pong.sheetutils import cache_csv_games_file, get_google_sheet
from pong.utils import print_title

# pylint: disable=unused-argument


def parser_func_download(**kwargs: Dict[str, Any]) -> Tuple[int, None]:
    """Default function for download parser"""
    cache_csv_games_file(
        _csv_bytes_output=get_google_sheet(),
    )
    return 0, None


def parser_func_rank(
    args: argparse.Namespace,
) -> Tuple[int, Tuple[List[Game], Dict[str, Player], Set[Club]]]:
    """Default function for rank parser"""

    # FIXME: make this into an annotation function? Easily, neatly re-usable & testable.
    if not args.skip_dl:  # pragma: no cover
        cache_csv_games_file(
            _csv_bytes_output=get_google_sheet(),
        )

    # Rate players, print rankings
    games, players, clubs = process_csv()
    func_rank(
        games=games,
        players=players,
        clubs=list(clubs),
        extended_titles=args.no_abbrev_titles,
    )

    # Optionally print match ups
    if args.matches:
        func_match_ups(players=players)

    # Optionally print the rating progress charts
    if args.graph:
        print_title("Rating progress charts")
        for p in players.values():  # pylint: disable=invalid-name
            print()
            print(p)
            print("Last 10:", [round(x.mu) for x in p.ratings[:10]])
            p.graph_ratings()

    return 0, (games, players, clubs)
