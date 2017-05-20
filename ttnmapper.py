#
# ttnmapper.py
#
# Implementation of a ttnmapper-node for LoPy.
# See http://ttnmapper.org and https://www.pycom.io/product/lopy for details.
#
# Copyright (C) 2017, Peter Affolter and Pascal Mainini
# Licensed under MIT license, see included file LICENSE or
# http://opensource.org/licenses/MIT
#
# History
# =======
#
# 2017-01-25    v.0.0.1     Initial Version, OTAA
#               v.0.0.2     Energy consumption optimized with timer alarms and 
#                           idle
# 2017-05-19    v.0.1.0     Refactored
#

import pycom
import time

from machine import Pin, UART, Timer
from nmea import NmeaParser


################################################################################
# Configuration and Constants
################################################################################

SEND_RATE       = 30        # Interval for position update + transmission (secs)

# GNSS Configuration
GNSS_TIMEOUT    = 5000      # Timeout for obtaining position (miliseconds)
GNSS_ENABLE_PIN = 'P8'
GNSS_UART_PORT  = 1
GNSS_UART_BAUD  = 9600

# Colors used for status LED
RGB_OFF         = 0x000000
RGB_POS_UPDATE  = 0x302000
RGB_POS_FOUND   = 0x003000
RGB_POS_NFOUND  = 0x300000
LED_TIMEOUT     = 0.2


################################################################################
# Function Definitions
################################################################################

def init_gnss():
    """Initialize the GNSS receiver"""

    enable = Pin(GNSS_ENABLE_PIN,  mode=Pin.OUT)
    enable(False)
    uart = UART(GNSS_UART_PORT, 9600)
    uart.init(GNSS_UART_BAUD,  bits=8,  parity=None,  stop=1)
    enable(True)

    return (uart, enable)

def gnss_position():
    """ Obtain current GNSS position.

    Returns a tuple (latitude,longitude,altitude,hdop) or None if
    no position obtained.
    """
    nmea = NmeaParser()
    start = time.ticks_ms()

    found = False
    while not found:
        if gnss_uart.any():
            nmea.update(gnss_uart.readline())
        if nmea.fix_stat & nmea.valid_sentence:
            found = True
        if  (time.ticks_diff(start,  time.ticks_ms()) > GNSS_TIMEOUT):
            return None

    return (nmea.latitude, nmea.longitude, nmea.altitude, nmea.hdop)
 
def update_task(alarmtrigger):
    """Periodically run task which tries to get current position and update
       ttnmapper"""
       
    pycom.rgbled(RGB_POS_UPDATE)
    time.sleep(LED_TIMEOUT)
    position = gnss_position()

    if position:
        (lat, lon, alt, hdop) = position
        print('Lat: {}, Lon: {}, Alt: {}, HDOP: {}'.format(lat,lon,alt,hdop))
        
        pycom.rgbled(RGB_POS_FOUND)

    else:
        print('No position obtained!')
        pycom.rgbled(RGB_POS_NFOUND)

    time.sleep(LED_TIMEOUT)
    pycom.rgbled(RGB_OFF)

    machine.idle()


################################################################################
# Main Program
################################################################################

print('ttnmapper -- Initializing...')

pycom.heartbeat(False)      # Turn off hearbeat LED

(gnss_uart, gnss_enable) = init_gnss()

alarm = Timer.Alarm(update_task, s=SEND_RATE,  periodic=True)

print('ttnmapper - Done!')
