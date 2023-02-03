# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 20:36:11 2023

@author: shane
"""

if __name__ == "__main__":
    print("SINGLES")
    print(f"Last updated: {datetime.utcnow()}")

    _sorted_players = filter_players(build_ratings())
    cache_ratings_csv_file(_sorted_players, singles=True)

    print_singles_matchups(_sorted_players)

    # Filter players with a highly uncertain rating
    _sorted_players = list(
        filter(lambda x: x.rating_singles.phi * 1.96 < 300, _sorted_players)
    )
    print_progresses(_sorted_players)
