# SPDX-FileCopyrightText: 2018 ladyada for Adafruit Industries
# SPDX-FileCopyrightText: 2022 johnrbnsn
#
# SPDX-License-Identifier: MIT

"""
`adafruit_lidarlite`
====================================================

A CircuitPython & Python library for Garmin LIDAR Lite sensors over I2C

* Author(s): ladyada, johnrbnsn

Implementation Notes
--------------------

**Hardware:**


**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

"""

# imports
import time
from adafruit_bus_device.i2c_device import I2CDevice
from digitalio import Direction
from micropython import const

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_LIDARLite.git"


_ADDR_DEFAULT = const(0x62)
_REG_ACQ_COMMAND = const(0x00)
_REG_DIST_MEAS_V3 = const(0x8F)
_REG_DIST_MEAS_V3HP = const(0x0F)
_REG_SIG_COUNT_VAL = const(0x02)
_REG_ACQ_CONFIG_REG = const(0x04)
_REG_THRESHOLD_BYPASS = const(0x1C)
_REG_STATUS = const(0x01)
_REG_UNIT_ID_HIGH = const(0x16)
_REG_UNIT_ID_LOW = const(0x17)
_REG_SIGNAL_STRENGTH = const(0x0E)
_REG_HEALTH_STATUS_V3HP = const(0x48)
_REG_POWER_CONTROL = const(0x65)
_REG_I2C_CONFIG = const(0x1E)
_REG_TEST_COMMAND = const(0x40)
_REG_CORR_DATA = const(0x52)

_CMD_RESET = const(0x00)
_CMD_DISTANCENOBIAS = const(0x03)
_CMD_DISTANCEWITHBIAS = const(0x04)
_CMD_DISTANCE_V3HP = const(0x03)
_NUM_DIST_BYTES = 2  # How many bytes is the returned distance measurement?

TYPE_V3 = "V3"
TYPE_V3HP = "V3HP"

CONFIG_DEFAULT = 0
CONFIG_SHORTFAST = 1
CONFIG_DEFAULTFAST = 2
CONFIG_MAXRANGE = 3
CONFIG_HIGHSENSITIVE = 4
CONFIG_LOWSENSITIVE = 5

"""Status Registers"""
# v3
STATUS_BUSY = 0x01
STATUS_REF_OVERFLOW = 0x02
STATUS_SIGNAL_OVERFLOW = 0x04
STATUS_NO_PEAK = 0x08
STATUS_SECOND_RETURN = 0x10
STATUS_HEALTHY = 0x20
STATUS_SYS_ERROR = 0x40

# v3 HP
STATUS_BUSY_V3HP = 0x01
STATUS_SIGNAL_OVERFLOW_V3HP = 0x02

# The various configuration register values, from arduino library
_LIDAR_CONFIGS = (
    (0x80, 0x08, 0x00),  # default
    (0x1D, 0x08, 0x00),  # short range, high speed
    (0x80, 0x00, 0x00),  # default range, higher speed short range
    (0xFF, 0x08, 0x00),  # maximum range
    (0x80, 0x08, 0x80),  # high sensitivity & error
    (0x80, 0x08, 0xB0),
)  # low sensitivity & error


class LIDARLite:
    """
    A driver for the Garmin LIDAR Lite laser distance sensor.

    Initialize the hardware for the LIDAR over I2C. You can pass in an
    optional reset_pin for when you call reset(). There are a few common
    configurations Garmin suggests: CONFIG_DEFAULT, CONFIG_SHORTFAST,
    CONFIG_DEFAULTFAST, CONFIG_MAXRANGE, CONFIG_HIGHSENSITIVE, and
    CONFIG_LOWSENSITIVE. For the I2C address, the default is 0x62 but if you
    pass a different number in, we'll try to change the address so multiple
    LIDARs can be connected. (Note all but one need to be in reset for this
    to work!)

    :param i2c_bus: The `busio.I2C` object to use. This is the only
                    required parameter.
    :param int address: (optional) The I2C address of the device to set
                        after initialization.
    """

    def __init__(
        self,
        i2c_bus,
        *,
        reset_pin=None,
        configuration=CONFIG_DEFAULT,
        address=_ADDR_DEFAULT,
        sensor_type=TYPE_V3,
    ):
        self.i2c_device = I2CDevice(i2c_bus, address)
        self._buf = bytearray(2)
        self._bias_count = 0
        self._reset = reset_pin
        time.sleep(0.5)
        self.configure(configuration)
        self._status = self.status
        self._sensor_type = sensor_type

    def reset(self):
        """Hardware reset (if pin passed into init) or software reset. Will take
        100 readings in order to 'flush' measurement unit, otherwise data is off."""
        # Optional hardware reset pin
        if self._reset is not None:
            self._reset.direction = Direction.OUTPUT
            self._reset.value = True
            self._reset.value = False
            time.sleep(0.01)
            self._reset.value = True
        else:
            try:
                self._write_reg(_REG_ACQ_COMMAND, _CMD_RESET)
            except OSError:
                print("OSError")
        time.sleep(1)
        # take 100 readings to 'flush' out sensor!
        for _ in range(100):
            try:
                self.read_distance_v3(True)
            except RuntimeError:
                print("RuntimeError")

    def configure(self, config):
        """Set the LIDAR desired style of measurement. There are a few common
        configurations Garmin suggests: CONFIG_DEFAULT, CONFIG_SHORTFAST,
        CONFIG_DEFAULTFAST, CONFIG_MAXRANGE, CONFIG_HIGHSENSITIVE, and
        CONFIG_LOWSENSITIVE."""
        settings = _LIDAR_CONFIGS[config]
        self._write_reg(_REG_SIG_COUNT_VAL, settings[0])
        self._write_reg(_REG_ACQ_CONFIG_REG, settings[1])
        self._write_reg(_REG_THRESHOLD_BYPASS, settings[2])

    def read_distance_v3(self, bias=False):
        """Perform a distance reading with or without 'bias'. It's recommended
        to take a bias measurement every 100 non-bias readings (they're slower)"""
        if bias:
            self._write_reg(_REG_ACQ_COMMAND, _CMD_DISTANCEWITHBIAS)
        else:
            self._write_reg(_REG_ACQ_COMMAND, _CMD_DISTANCENOBIAS)
        dist = self._read_reg(_REG_DIST_MEAS_V3, _NUM_DIST_BYTES)
        if self._status & (STATUS_NO_PEAK | STATUS_SECOND_RETURN):
            if self._status & STATUS_NO_PEAK:
                raise RuntimeError("Measurement failure STATUS_NO_PEAK")
            if self._status & STATUS_SECOND_RETURN:
                raise RuntimeError("Measurement failure STATUS_NO_PEAK")
            raise RuntimeError("Some other runtime error")

        if (self._status & STATUS_SYS_ERROR) or (not self._status & STATUS_HEALTHY):
            raise RuntimeError("System failure")
        return dist[0] << 8 | dist[1]

    def read_distance_v3hp(self):
        """Perform a distance measurement for the v3 HP sensor"""
        # Any non-zero value written to _REG_ACQ_COMMAND will start a reading on v3HP, no bias vs.
        #   non-bias
        self._write_reg(_REG_ACQ_COMMAND, _CMD_DISTANCEWITHBIAS)
        dist = self._read_reg(_REG_DIST_MEAS_V3HP, _NUM_DIST_BYTES)
        return dist[0] << 8 | dist[1]

    @property
    def correlation_data(self):
        """Reads correlation data"""
        # TODO: How to translate correlation data property?
        corr_data = self._read_reg(_REG_CORR_DATA, 2)
        return corr_data[0] << 8 | corr_data[1]

    @property
    def test_command(self):
        """Reads the test command"""
        return self._read_reg(_REG_TEST_COMMAND, 1)[0]

    @property
    def i2c_config(self):
        """Reads the I2C config"""
        return self._read_reg(_REG_I2C_CONFIG, 1)[0]

    @property
    def power_control(self):
        """Reads the power control register"""
        return self._read_reg(_REG_POWER_CONTROL, 1)[0]

    @property
    def health_status(self):
        """Reads health status for v3HP (not available on v3, will return -1)"""
        if self._sensor_type == TYPE_V3HP:
            return self._read_reg(_REG_HEALTH_STATUS_V3HP, 1)[0]

        return -1

    @property
    def signal_strength(self):
        """Reads the signal strength of the last measurement"""
        return self._read_reg(_REG_SIGNAL_STRENGTH, 1)[0]

    @property
    def unit_id(self):
        """Reads the serial number of the unit"""
        high_byte = self._read_reg(_REG_UNIT_ID_HIGH, 1)
        low_byte = self._read_reg(_REG_UNIT_ID_LOW, 1)

        return high_byte[0] << 8 | low_byte[0]

    @property
    def distance(self):  # pylint: disable=R1710
        """The measured distance in cm. Will take a bias reading every 100 calls"""
        self._bias_count -= 1

        if self._bias_count < 0:
            self._bias_count = 100  # every 100 reads, check bias
        if self._sensor_type == TYPE_V3:
            return self.read_distance_v3(self._bias_count <= 0)
        if self._sensor_type == TYPE_V3HP:
            return self.read_distance_v3hp()

        # If no sensor type has been identified, return a negative distance as an error
        return -1.0

    @property
    def status(self):
        """The status byte, check datasheet for bitmask"""
        buf = bytearray([_REG_STATUS])
        with self.i2c_device as i2c:
            i2c.write_then_readinto(buf, buf)
        return buf[0]

    def _write_reg(self, reg, value):
        self._buf[0] = reg
        self._buf[1] = value
        with self.i2c_device as i2c:
            # print("Writing: ", [hex(i) for i in self._buf])
            i2c.write(self._buf)
        time.sleep(0.001)  # there's a delay in arduino library

    def _read_reg(self, reg, num):
        while True:
            self._status = self.status
            if not self._status & STATUS_BUSY:
                break
        # no longer busy
        self._buf[0] = reg
        with self.i2c_device as i2c:
            i2c.write_then_readinto(self._buf, self._buf, out_end=1, in_end=num)
        # print("Read from ", hex(reg), [hex(i) for i in self._buf])
        return self._buf
