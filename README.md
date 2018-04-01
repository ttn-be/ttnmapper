# Introduction

This is an implementation of a mapper node for [ttnmapper.org](http://ttnmapper.org) written in Python for the [LoPy MCU](https://www.pycom.io/product/lopy). It can be used for finding gateways of [The Things Network (TTN)](https://www.thethingsnetwork.org) and determine their reach.

# Setup

To get your own mapper up and running, the following steps are required:

1. Setup Hardware
2. Configure WLAN
3. Install software
4. Obtain TTN application key
5. Have fun!

## Hardware Setup

For mapping, an additional *GNSS (GPS) receiver* (not part of LoPy) is required, which supports communication using NMEA-0183 and
provides position data with the `$GPGGA` sentence.
A connection to this receiver is expected on UART 1 (refer to [LoPy pinout](https://docs.pycom.io/pycom_esp32/_downloads/lopy_pinout.pdf)) with 9600 Baud; this may be adjusted in `config.py`.
Additionally, an enable pin (defaults to `P8`) can be wired, which resets the receiver upon restart of the application.

## Configure WLAN

By default, WLAN is turned off to save power. However, to update (using FTP) or interact (using telnet) with the LoPy, a wireless connection may be used. By pulling one of the following pins to *ground*, the LoPy may be configured with enabled WLAN as follows:

* `P11` enables WLAN and joins a network. SSID and authentication must be configured in `config.py` first (refer to [docs](https://docs.pycom.io/pycom_esp32/library/network.WLAN.html) for more information).
* `P12` enables an access point with SSID `ttn-be-mapper` and WPA2 password `reppam-eb-ntt` (SSID backwards)

Leaving the pins open disables the WLAN. By setting `WLAN_MODE` in `config.py` to *'sta'* (=P11) or *'ap'* (=P12), the respective setting may be configured permanently.

## Install Software

To install ttnmapper, simply upload all Python files (ending in `.py`) to your LoPy's `flash` directory.
If you want to join your own WLAN network, be sure to adjust the parameters in `config.py` first, as described before!

## Obtain TTN application key

[ttnmapper.org](http://ttnmapper.org) retrieves the data required for building the map from specific TTN applications.
Setting up an application on TTN and having ttnmapper.org connecting to it is out of scope (see the [ttnmapper FAQ](http://ttnmapper.org/faq.php) for details how to do that).

ttnmapper ist preconfigured for the *ttn-be* mapper application (EUI `70B3D57EF0001ED4`), however a per-device Key must be generated before data can be transmitted to the application. In order to obtain a key, please send the device EUI of your LoPy, which is displayed during the boot process, to `thethingsnetwork [at] bfh [dot] ch`. The obtained key must then be set in `config.py`.

Having obtained your key, everything should now be ready and you can start searching TTN gateways in your neighbourhood!

# Further Tweaks

## Status LED Codes

ttnmapper displays its current status using the built-in RGB LED of the LoPy. Two main states can be distinguished:

* Joining the TTN network: LED is cycling between blue and off until the network has been joined
* Mapping position: a periodical task tries to obtain the position from the GNSS receiver. During that task, the LED is yellow. If position has been determined, it quickly turns green, otherwise red.

## Update Interval

In order to stay within TTN's [fair use policy](https://www.thethingsnetwork.org/wiki/LoRaWAN/Duty-Cycle), a total sending time of 30 seconds per day must not be exceeded. Position transmission of ttnmapper takes roughly 56.6 ms, leading to a predefined interval of 180 seconds (=480 messages / day or 28.8 seconds). This may be adjusted in `config.py`.

## Disabling Transmissions

It may be desirable to completly disable position transmission to TTN. There are multiple options for this:

* Pulling pin `P9` to *ground* and reset the LoPy. This will prevent joining any LoRa network at all.
* Setting `LORA_ENABLE` to *False* in `config.py`.
* Disabling the periodically run transmission task interactively: In the LoPy Python shell (via telnet or serial connection), enter `mapper.cancel()`

# Version History

## 1.0.0 (2017-06-15)
* Initial release
