# The MIT License (MIT)
#
# Copyright (c) 2018 ladyada for adafruit industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_lidarlite`
====================================================

A CircuitPython & Python library for Garmin LIDAR Lite sensors over I2C

* Author(s): ladyada

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
CONFIG_DEFAULT = 0
CONFIG_SHORTFAST = 1
CONFIG_DEFAULTFAST = 2
CONFIG_MAXRANGE = 3
CONFIG_HIGHSENSITIVE = 4
CONFIG_LOWSENSITIVE = 5
_REG_ACQ_COMMAND = const(0x00)
_CMD_RESET = const(0)
_CMD_DISTANCENOBIAS = const(3)
_CMD_DISTANCEWITHBIAS = const(4)

STATUS_BUSY = 0x01
STATUS_REF_OVERFLOW = 0x02
STATUS_SIGNAL_OVERFLOW = 0x04
STATUS_NO_PEAK = 0x08
STATUS_SECOND_RETURN = 0x10
STATUS_HEALTHY = 0x20
STATUS_SYS_ERROR = 0x40

                         
# The various configuration register values
_configurations = ((0x80, 0x08, 0x00),)

class LIDARLite:
    """
    A driver for the Garmin LIDAR Lite laser distance sensor.
    :param i2c_bus: The `busio.I2C` object to use. This is the only
    required parameter.
    :param int address: (optional) The I2C address of the device to set after initialization.
    """

    def __init__(self, i2c_bus, *, reset_pin=None, configuration=CONFIG_DEFAULT, address=_ADDR_DEFAULT):
        self.i2c_bus = i2c_bus
        self.i2c_device = I2CDevice(i2c_bus, address)
        self._buf = bytearray(2)
        time.sleep(0.5)
        self.configure(configuration)
    
    def reset(self):
        # Optional hardware reset pin
        if reset_pin is not None:
            reset_pin.direction = Direction.OUTPUT
            reset_pin.value = True
            reset_pin.value = False
            time.sleep(0.01)
            reset_pin.value = True
        else:
            try:
                self._write_reg(_REG_ACQ_COMMAND, _CMD_RESET)
            except OSError:
                pass   # it doesnt respond well once reset
        time.sleep(3)

    def configure(self, config):
        settings = _configurations[config]
        self._write_reg(0x02, settings[0])
        self._write_reg(0x04, settings[1])
        self._write_reg(0x1c, settings[2])

    def get_distance(self):

        # write & wait
        with self.i2c_device as i2c:
            i2c.write(bytes([0, 4]))
        time.sleep(0.02)  # in arduino library

    def read_distance(self, bias=False):
        if bias:
            self._write_reg(_REG_ACQ_COMMAND, _CMD_DISTANCEWITHBIAS)
        else:
            self._write_reg(_REG_ACQ_COMMAND, _CMD_DISTANCENOBIAS)
        d = self._read_reg(0x8F, 2)
        if self._status & (STATUS_REF_OVERFLOW | STATUS_SIGNAL_OVERFLOW | STATUS_NO_PEAK | STATUS_SECOND_RETURN):
            raise RuntimeError("Measurement failure")
        if (self._status & STATUS_SYS_ERROR) or (not self._status & STATUS_HEALTHY):
            raise RuntimeError("System failure")
        dist = d[0] << 8 | d[1]
        return dist

    @property
    def distance(self):
        #return self.read_distance()  # try to read the distance
        self._write_reg(0x00, 0x04)
        buf = self._read_reg(0x8F, 2)
        #with self.i2c_device as i2c:
        #    buf = bytearray(2)
        #    i2c.write(bytes([0x8F]))
        #    i2c.readinto( buf)
        return buf[0] << 8 | buf[1]
  
    @property
    def bias_distance(self):
        return self.read_distance(True)


    @property
    def status(self):
        buf = bytearray([0x1])
        with self.i2c_device as i2c:
            i2c.write(buf)
            i2c.readinto(buf)
        print("Status: ", [hex(i) for i in buf])
        return buf[0]

    def _write_reg(self, reg, value):        
        self._buf[0] = reg
        self._buf[1] = value
        with self.i2c_device as i2c:
            #print("Writing: ", [hex(i) for i in self._buf])
            i2c.write(self._buf)
        time.sleep(0.02)  # in arduino library

    def _read_reg(self, reg, len):
        while True:
            self._status = self.status
            if not self._status & STATUS_BUSY:
                break
        # no longer busy
        self._buf[0] = reg
        with self.i2c_device as i2c:
            i2c.write(self._buf, end=1)
            i2c.readinto(self._buf, end=len)
        #print("Read from ", hex(reg), [hex(i) for i in self._buf])
        return self._buf
