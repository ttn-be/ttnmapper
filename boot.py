# boot.py -- run on boot-up
import os
import machine
from machine import Pin
from network import WLAN, Bluetooth
from config import *

# Configure USB Serial
uart = machine.UART(0, 115200)
os.dupterm(uart)

# Turn off Bluetooth
bt = Bluetooth()
bt.deinit()

# Configure WLAN
wlan = WLAN()
wlan.deinit()

# Disable debug logging by default, may be enabled later on in config.py
DEBUG = False


def init_wlan_ap():
    """Set up WPA2 protected access point with SSID 'ttn-be-mapper'
    and password 'reppam-eb-ntt'."""

    print('WLAN: AP mode')
    wlan.init(mode=WLAN.AP,
              ssid='ttn-be-mapper',
              auth=(WLAN.WPA2, 'reppam-eb-ntt'),
              channel=7,
              antenna=WLAN.INT_ANT)


def init_wlan_sta():
    """Connect to wifi network specified in configuration."""

    print('WLAN: STA mode')
    wlan.init(mode=WLAN.STA)
    if not wlan.isconnected():
        wlan.connect(WLAN_SSID, auth=WLAN_AUTH, timeout=5000)
        while not wlan.isconnected():
            machine.idle()  # save power while waiting


if not Pin('P11', mode=Pin.IN, pull=Pin.PULL_UP)():
    init_wlan_sta()
elif not Pin('P12', mode=Pin.IN, pull=Pin.PULL_UP)():
    init_wlan_ap()
elif WLAN_MODE.lower() == 'sta':
    init_wlan_sta()
elif WLAN_MODE.lower() == 'ap':
    init_wlan_ap()
else:
    print('WLAN: Disabled')
