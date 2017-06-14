# LoPy ttnmapper

This is an implementation of a mapper node for [ttnmapper.org](http://ttnmapper.org) written in Python for the [LoPy MCU](https://www.pycom.io/product/lopy).

To get your own mapper up and running, the following steps are required:

1. Setup Hardware
1. Configure WLAN
2. Obtain TTN application key

## Hardware Setup

For mapping, an additional *GNSS (GPS) device* (not part of LoPy) is required, whichs supports communication using NMEA-0183 and
provides position data with the `$GPGGA` sentence.
A connection to the GNSS device is expected using UART 1 (refer to [LoPy Pinout](https://docs.pycom.io/pycom_esp32/_downloads/lopy_pinout.pdf)) with 
9600 Baud, this may be adjusted in `ttnmapper.py`.
Additionally, the application provides a pin for enabling/disabling the GNSS device (defaults to `P8`).

