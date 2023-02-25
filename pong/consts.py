#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 16:06:42 2023

@author: shane
"""

import os

from pong import PROJECT_ROOT

_PROB_GAME_TO_POINT_FILE = os.path.join(
    PROJECT_ROOT, "resources", "prob_game_to_point.txt"
)

with open(_PROB_GAME_TO_POINT_FILE, encoding="utf-8") as _f:
    GAME_PERCENT_TO_POINT_PROB = [float(x) for x in _f.readlines()]
