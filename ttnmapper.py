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

import array
import pycom
import socket
import time

from binascii import hexlify, unhexlify
from machine import Pin, UART, Timer, idle
from network import LoRa
from nmea import NmeaParser
from config import *

###############################################################################
# Configuration and Constants
###############################################################################

# Colors used for status LED
RGB_OFF         = 0x000000
RGB_POS_UPDATE  = 0x403000
RGB_POS_FOUND   = 0x004000
RGB_POS_NFOUND  = 0x400000
RGB_LORA_JOIN   = 0x000040
RGB_LORA_JOINED = 0x004000
LED_TIMEOUT     = 0.2


###############################################################################
# Function Definitions
###############################################################################

def log(msg):
    """Helper method for logging messages"""
    print('ttnmapper: {}'.format(msg))


def init_gnss():
    """Initialize the GNSS receiver"""

    log('Initializing GNSS...')

    enable = Pin(GNSS_ENABLE_PIN, mode=Pin.OUT)
    enable(False)
    uart = UART(GNSS_UART_PORT)
    uart.init(GNSS_UART_BAUD, bits=8, parity=None, stop=1)
    enable(True)

    log('Done!')

    return (uart, enable)


def init_lora():
    """Initialize LoRaWAN connection"""

    lora_disabled = not Pin(LORA_ENABLE_PIN, mode=Pin.IN, pull=Pin.PULL_UP)()
    if not LORA_ENABLE or lora_disabled:
        log('LoRa disabled!')
        return (None, None)

    lora = LoRa(mode=LoRa.LORAWAN)
    log('Initializing LoRaWAN, DEV EUI: {} ...'.format(hexlify(lora.mac())
        .decode('ascii').upper()))

    if not LORA_APP_KEY:
        log('ERROR: LoRaWAN APP KEY not set!')
        log('Send your DEV EUI to thethingsnetwork@bfh.ch to obtain one.')
        return (None, None)

    pycom.rgbled(RGB_LORA_JOIN)

    lora.join(activation=LoRa.OTAA, auth=(unhexlify(LORA_APP_EUI),
              unhexlify(LORA_APP_KEY)), timeout=0)

    while not lora.has_joined():
        log('Joining...')
        pycom.rgbled(RGB_OFF)
        time.sleep(LED_TIMEOUT)
        pycom.rgbled(RGB_LORA_JOIN)
        time.sleep(2.5)

    pycom.rgbled(RGB_OFF)

    # Setup socket
    sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    sock.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)      # Set data rate
    sock.setblocking(False)

    log('Done!')
    return (lora, sock)


def gnss_position():
    """Obtain current GNSS position.
    If a position has been obtained, returns an instance of NmeaParser
    containing the data. Otherwise, returns None."""

    nmea = NmeaParser()
    start = time.ticks_ms()

    while time.ticks_diff(start, time.ticks_ms()) < GNSS_TIMEOUT:
        if nmea.update(gnss_uart.readall()):
            log('Current position: {}'.format(nmea))
            return nmea

    log('No position: {}'.format(nmea.error))
    return None


def transmit(nmea):
    """Encode current position, altitude and hdop and send it using LoRaWAN"""

    data = array.array('B', [0, 0, 0, 0, 0, 0, 0, 0, 0])

    lat = int(((nmea.latitude + 90) / 180) * 16777215)
    data[0] = (lat >> 16) & 0xff
    data[1] = (lat >> 8) & 0xff
    data[2] = lat & 0xff

    lon = int(((nmea.longitude + 180) / 360) * 16777215)
    data[3] = (lon >> 16) & 0xff
    data[4] = (lon >> 8) & 0xff
    data[5] = lon & 0xff

    alt = int(nmea.altitude)
    data[6] = (alt >> 8) & 0xff
    data[7] = alt & 0xff

    hdop = int(nmea.hdop * 10)
    data[8] = hdop & 0xff

    message = bytes(data)
    count = sock.send(message)

    log('Message sent: {} ({} bytes)'.format(hexlify(message).upper(), count))


def update_task(alarmtrigger):
    """Periodically run task which tries to get current position and update
       ttnmapper"""

    pycom.rgbled(RGB_POS_UPDATE)
    time.sleep(LED_TIMEOUT)
    pos = gnss_position()

    if pos:
        pycom.rgbled(RGB_POS_FOUND)
        transmit(pos)
    else:
        pycom.rgbled(RGB_POS_NFOUND)

    time.sleep(LED_TIMEOUT)
    pycom.rgbled(RGB_OFF)

    idle()


###############################################################################
# Main Program
###############################################################################

log('Starting up...')

pycom.heartbeat(False)      # Turn off hearbeat LED

(gnss_uart, gnss_enable) = init_gnss()
(lora, sock) = init_lora()

if lora:
    mapper = Timer.Alarm(update_task, s=LORA_SEND_RATE, periodic=True)

log('Startup completed')
