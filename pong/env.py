# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 17:14:19 2023

@author: shane
Loads ENVIRONMENT VARIABLES from file: `.env`
"""
import os

import dotenv

dotenv.load_dotenv(verbose=True)

# TODO: support inverse too? Inactive players
PLAYERS_PRESENT = set(os.environ.get("PLAYERS").split())
