#
# nmea.py
#
# Minimalistic NMEA-0183 message parser
#
# Copyright (C) 2017, Peter Affolter and Pascal Mainini
# Licensed under MIT license, see included file LICENSE or
# http://opensource.org/licenses/MIT
#
# History
# =======
#
# 2017-01-25    v.0.1.0     Initial Version
# 2017-05-19    v.0.1.1     Refactored
#

import utime

class NmeaParser:
    """NMEA sentence parser. update() parses a sentence and stores relevant
    GPS data and statistics as attributes."""

    def __init__(self):
        """Initializes attributes to useful default values."""

        # Raw data segments
        self.nmea_segments = []
        self.error = None

        # General data
        self.timestamp = ()
        self.fix_status = 0
        self.fix_time = 0
        self.satellites_in_use = 0
        self.hdop = 0.0

         # Position data
        self.altitude = 0.0
        self.latitude = 0.0
        self.longitude = 0.0

    def __str__(self):
        """Return meaningful string representation"""

        return 'T: {}:{}:{}, Lat: {}, Lon: {}, Alt: {}, Fix: {}, Sat: {}, HDOP: {}'.format(
            self.timestamp[0], self.timestamp[1], self.timestamp[2], self.latitude, 
            self.longitude, self.altitude, self.fix_status, self.satellites_in_use, self.hdop)

    def update(self,  sentence):
        """Parses a given NMEA sentence string (terminated with \\r\\n) and updates attributes.
        Returns True on success, False otherwise. Errors are stored in self.error."""

        # Split data / checksum
        try:
            (data, checksum) = sentence.split('*')
            checksum = int(checksum[:2], 16)        # first two bytes only, skip \r\n
        except:
            self.error = 'Missing or invalid checksum.'
            return False

        # Calculate checksum
        calculated = 0
        for b in bytes(data[1:], 'ascii'):          # $ is not part of checksum
            calculated ^= b

        if checksum != calculated:
            self.error = 'Invalid checksum.'
            return False

        # Split and perform further checks

        self.nmea_segments = data.split(',')

        if self.nmea_segments[0] != '$GPGGA':
            self.error = 'Unsupported sentence.'
            return False

        if len(self.nmea_segments) < 10:
            self.error = 'Incomplete sentence.'
            return False

        if len(self.nmea_segments[1]) == 0:
            self.error = 'Time not synchronized.'
            return False

        # Retrieve all relevant data
        try:
            # UTC Timestamp
            utc_string = self.nmea_segments[1]
            self.timestamp = ( int(utc_string[0:2]), int(utc_string[2:4]), float(utc_string[4:]) )

            # Other data
            self.fix_status = int(self.nmea_segments[6])
            self.satellites_in_use = int(self.nmea_segments[7])
            self.hdop = float(self.nmea_segments[8])        # Horizontal Dilution of Precision

            if self.fix_status == 0:
                self.error = 'No fix obtained.'
                return False

            self.fix_time = utime.time()

            # Altitude
            self.altitude = float(self.nmea_segments[9])

            # Latitude
            l = self.nmea_segments[2]
            lat_degs = float(l[0:2])
            lat_mins = float(l[2:])
            self.latitude = lat_degs + (lat_mins/60)

            # Longitude
            l = self.nmea_segments[4]
            lon_degs = float(l[0:3])
            lon_mins = float(l[3:])
            self.longitude = lon_degs + (lon_mins/60)

        except Exception as err:
            self.error = err
            return False
        else:
            self.error = None
            return True

