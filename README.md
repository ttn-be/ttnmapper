# Introduction

This is an implementation of a mapper node for [ttnmapper.org](http://ttnmapper.org) written in Python for the [LoPy MCU](https://www.pycom.io/product/lopy). It can be used for finding gateways of [The Things Network (TTN)](https://www.thethingsnetwork.org) and determine their reach.

# Setup

To get your own mapper up and running, the following steps are required:

1. Setup hardware
2. Configure WLAN
3. Install software
4. Join the TTN network
6. Have fun!

## Setup Hardware

For mapping, an additional *GNSS (GPS) receiver* (not part of LoPy) is required, which supports communication using NMEA-0183 and
provides position data with the `$GPGGA` sentence.
A connection to this receiver is expected on UART 1 (refer to [LoPy pinout](https://docs.pycom.io/chapter/datasheets/downloads/lopy-pinout.pdf)) with 9600 Baud; this may be adjusted in `config.py`.
Additionally, an enable pin (defaults to `P8`) can be wired, which resets the receiver upon restart of the application.
Setting  `DEBUG` to *True* in `config.py` enables logging of the data received from the GNSS receiver to LoPy's USB console.

## Configure WLAN

By default, WLAN is turned off to save power. However, to update (using FTP) or interact (using telnet) with the LoPy, a wireless connection may be used. By pulling one of the following pins to *ground*, the LoPy is configured with enabled WLAN as follows:

* `P11` enables WLAN and joins a network. SSID and authentication must be configured in `config.py` first (refer to [LoPy docs](https://docs.pycom.io/chapter/firmwareapi/pycom/network/wlan.html) for a description of possible values for `WLAN_AUTH`).
* `P12` enables an access point with SSID `ttn-be-mapper` and WPA2 password `reppam-eb-ntt` (SSID backwards)

Leaving the pins unconnected disables the WLAN. By setting `WLAN_MODE` in `config.py` to *'sta'* (=P11) or *'ap'* (=P12), the respective setting may be configured permanently.

## Install Software

To install ttnmapper, simply upload all Python files (ending in *.py*) to your LoPy's `flash` directory.

*If you want to join your own WLAN network, be sure to adjust the parameters in `config.py` first, as described above!*

## Join the TTN network

There are two possibilities to join the TTN network and transmit position data to ttnmapper.org:

### Use the *ttn-be* mapper application

[ttnmapper.org](http://ttnmapper.org) retrieves the data required for building the map from specific TTN applications or using TTN *integrations*. The default `config.py` provided with this software is preconfigured for the *ttn-be* mapper application (EUI `70B3D57EF0001ED4`). In order to use this application, a per-device Key must be generated before any data can be transmitted. To obtain a key, please send the device EUI of your LoPy, which is displayed during the boot process, to `thethingsnetwork [at] bfh [dot] ch`. The obtained key must then be set as `LORA_OTAA_KEY` in `config.py`.

### Set up your own TTN application

If you do not want to use the *ttn-be* application, you can set up your own using the TTN console and configure the parameters in `config.py` accordingly, depending on *ABP* or *OTAA* activation of your device. [This decoder](https://github.com/ttn-be/gps-node-examples/blob/master/Sodaq/sodaq-one-ttnmapper/decoder.js) works for the transmitted data and can be deployed in the TTN console. However, setting up and configuring a TTN application for ttnmapper.org is out of scope of this documentation, see the [ttnmapper FAQ](http://ttnmapper.org/faq.php) for details on how to do that.


# Further Tweaks

## Status LED Codes

ttnmapper displays its current status using the built-in RGB LED of the LoPy. Two main states can be distinguished:

* Joining the TTN network: LED is cycling between blue and off until the network has been joined using OTAA activation. If ABP activation is used, the LED blinks three times briefly in blue during start of the LoPy.
* Mapping position: a periodical task tries to obtain the position from the GNSS receiver. While reading data from the GNSS receiver, the LED is yellow. If position could have been determined, it shortly turns green, otherwise red. If a position was determined, it is transmitted using LoRa. During this transmission, the LED is blue and turns off again afterwards.

## Update Interval

In order to stay within TTN's [fair use policy](https://www.thethingsnetwork.org/wiki/LoRaWAN/Duty-Cycle), a total sending time of 30 seconds per day must not be exceeded. Position transmission of ttnmapper takes roughly 56.6 ms, leading to a predefined interval of 180 seconds (=480 messages / day or 28.8 seconds). This may be adjusted in `config.py`.

## Disabling Transmissions

It may be desirable to completly disable position transmission to TTN. There are multiple options for this:

* Pulling pin `P9` to *ground* and reset the LoPy. This will prevent joining any LoRa network at all.
* Setting `LORA_MODE` to *'off'* in `config.py`.
* Disabling the transmission task interactively: In the LoPy Python shell (via telnet or serial connection), type *mapper.cancel()*

# Version History

## 1.1.0 (2018-04-10)
* Bugfixes
    * Provide negative coordinates if on southern or western hemisphere
    * Position-independent parsing of $GPGGA GNSS sentence
* Improvements
    * Support for ABP connection to TTN (additionally to OTAA)
    * All relevant settings can now be configured in `config.py`
    * Buffer-based I/O to GNSS receiver, no read-loop with timeout anymore
    * `DEBUG`-option for logging raw output of GNSS receiver

## 1.0.0 (2017-06-15)
* Initial release
