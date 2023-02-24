***************
 Pong rankings
***************

.. image:: https://github.com/nutratech/pong_ratings/actions/workflows/test.yml/badge.svg
  :target: https://github.com/nutratech/pong_ratings/actions/workflows/test.yml
  :alt: Test status unknown

Link to the Google Sheet
########################

https://docs.google.com/spreadsheets/d/1evcgUzJ5hO55RYshc3dH-EmzZfor58t0qPB-zp8iw4A/edit#gid=605912978


Setup (Linux)
#############

Install ``venv``.

.. code-block:: bash

  sudo apt install python3-venv

Set up ``venv``. Install ``pip`` dependencies and ``glicko2`` submodule.

.. code-block:: bash

  make init deps


Running
#######

Output the rankings and fairest match ups by running the main script.

Requires internet connection, as it currently fetches the Google Sheet every
time.

.. code-block:: bash

  ./singles.py

  ./doubles.py


Match ups for given players
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can run the top-level script, e.g.

.. code-block:: bash

  # Singles
  ./matchups.py benji norm

  # Doubles
  PONG_DOUBLES=1 ./matchups.py brandon thomas mal shane norm amos benji

**NOTE:** You can also run the script without player name arguments. Just set
the ``PLAYERS`` variable in the ``.env`` file, (see: "Filtering Players").

You can switch between modes by setting ``DOUBLES=1`` in the ``.env`` file.


Filtering Players
~~~~~~~~~~~~~~~~~

When there are too many doubles pairings, you can filter by present players
only.

Add this to a ``.env`` file.

.. code-block:: bash

  PONG_PLAYERS=player1 player2 player3 player4


TODO
####

- Test on Windows
