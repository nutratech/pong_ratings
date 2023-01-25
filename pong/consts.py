# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 16:06:42 2023

@author: shane
"""

import json
import os

from pong import PROJECT_ROOT

with open(os.path.join(PROJECT_ROOT, "resources", "prob_game_to_point.json")) as _f:
    GAME_PERCENT_TO_POINT_PROB = json.load(_f)
