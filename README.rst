***************
 Pong rankings
***************

.. image:: https://github.com/nutratech/pong_ratings/actions/workflows/test.yml/badge.svg
  :target: https://github.com/nutratech/pong_ratings/actions/workflows/test.yml
  :alt: Test status unknown

Link to the Google Sheet
########################

https://docs.google.com/spreadsheets/d/1evcgUzJ5hO55RYshc3dH-EmzZfor58t0qPB-zp8iw4A/edit#gid=757272539


Setup
#####

Install ``venv``.

.. code-block:: bash

  python3 -m venv .venv
  source .venv/bin/activate
  # or with direnv: direnv allow

Install ``pip`` dependencies and ``glicko2`` submodule.

.. code-block:: bash

  pip install -r requirements.txt
  git submodule update --init


Running
#######

Output the rankings and fairest matchings by running the main script.

Requires internet connection, as it currently fetches the Google Sheet every
time.

.. code-block:: bash

  ./singles.py

  ./doubles.py

  # Singles
  ./matchups.py benji norm

  # Doubles
  PONG_DOUBLES=1 ./matchups.py shane mal norm amos benji


Match ups for given players
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can run the top-level script, e.g.

.. code-block:: bash

  ./matchups.py brandon shane benji amos

**NOTE:** You can also run the script without player name arguments. Just set
the ``PLAYERS`` variable as in the above section ("Filtering Players").

You can switch between modes by setting ``DOUBLES=1`` in the ``.env`` file.


Filtering Players
~~~~~~~~~~~~~~~~~

When there are too many doubles pairings, you can filter by present players
only.

Add this to a ``.env`` file.

.. code-block:: bash

  PONG_PLAYERS=player1 player2 player3 player4
