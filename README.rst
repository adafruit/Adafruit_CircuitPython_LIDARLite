Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-lidarlite/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/lidarlite/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://discord.gg/nBQh6qu
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_LIDARLite/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_LIDARLite/actions/
    :alt: Build Status

A CircuitPython & Python library for Garmin LIDAR Lite sensors over I2C

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Installing from PyPI
====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-lidarlite/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-lidarlite

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-lidarlite

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install adafruit-circuitpython-lidarlite

Usage Example
=============

.. code-block:: python

	import time
	import board
	import busio
	import adafruit_lidarlite

	# Create library object using our Bus I2C port
	i2c = busio.I2C(board.SCL, board.SDA)

	# Default configuration, with only i2c wires
	sensor = adafruit_lidarlite.LIDARLite(i2c)

	while True:
    	    try:
                # We print tuples so you can plot with Mu Plotter
                print((sensor.distance,))
    	    except RuntimeError as e:
                # If we get a reading error, just print it and keep truckin'
                print(e)
    	    time.sleep(0.01) # you can remove this for ultra-fast measurements!

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_LIDARLite/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
