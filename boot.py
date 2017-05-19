# boot.py -- run on boot-up
import os
import machine
from network import WLAN, Bluetooth

# Configure USB Serial
uart = machine.UART(0, 115200)
os.dupterm(uart)

# Turn off Bluetooth
bt = Bluetooth()
bt.deinit()

# Configure WLAN
#wlan = WLAN()
#if machine.reset_cause() != machine.SOFT_RESET:
#    wlan.init(mode=WLAN.STA)
#
#if not wlan.isconnected():
#    wlan.connect(""" YOUR SETTINGS HERE """, timeout=5000)
#    while not wlan.isconnected():
#        machine.idle()

