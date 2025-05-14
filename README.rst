Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-lidarlite/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/lidarlite/en/latest/
    :alt: Documentation Status

.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_LIDARLite/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_LIDARLite/actions/
    :alt: Build Status

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

A CircuitPython & Python library for Garmin LIDAR Lite sensors over I2C

**Does not work with Lidar Lite v4 at this time, no ETA when it may be added - PRs accepted!**

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
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install adafruit-circuitpython-lidarlite

Usage Examples
==============

V3 Example
----------

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


V3 HP Example
-------------

.. code-block:: python

    import time
    import busio
    import board
    import adafruit_lidarlite

    i2c = busio.I2C(board.SCL, board.SDA)

    sensor = adafruit_lidarlite.LIDARLite(i2c, sensor_type=adafruit_lidarlite.TYPE_V3HP)

    while True:
        try:
            print(f"Sensor ID#: {sensor.unit_id}")
            print(f"Distance = {sensor.distance}")
            print(f"  Strength: {sensor.signal_strength}")
        except RuntimeError as e:
            print(e)
        try:
            print(f"Status: 0b{sensor.status:b}")
            print(f"  Busy: {bool(sensor.status & adafruit_lidarlite.STATUS_BUSY_V3HP)}")
            print(f"  Overflow: {bool(sensor.status & adafruit_lidarlite.STATUS_SIGNAL_OVERFLOW_V3HP)}")
            print(f"  Health: 0b{sensor.health_status:b}")
            print(f"  Power Control: 0b{sensor.power_control:b}")
            print(f"  I2C Config: 0b{sensor.i2c_config:b}")
            print(f"  Test Command: 0b{sensor.test_command:b}")
            print(f"  Correlation: 0b{sensor.correlation_data}")
        except RuntimeError as e:
            print(e)

        print()
        time.sleep(1)

Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/lidarlite/en/latest/>`_.

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_LIDARLite/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
