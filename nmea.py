#
# nmea.py
#
# Minimalistic NMEA-0183 message parser
#
# Copyright (C) 2017, Peter Affolter and Pascal Mainini
# Licensed under MIT license, see included file LICENSE or
# http://opensource.org/licenses/MIT
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

        return 'T: {}:{}:{}, '.format(
            self.timestamp[0], self.timestamp[1], self.timestamp[2]) \
            + 'Lat: {}, Lon: {}, Alt: {}, '.format(
            self.latitude, self.longitude, self.altitude) \
            + 'Fix: {}, Sat: {}, HDOP: {}'.format(
            self.fix_status, self.satellites_in_use, self.hdop)

    def update(self, data):
        """Tries to find a $GPGGA sentence in the data and parses it, storing
        relevant data as attributes.
        Returns True on success, False otherwise.
        Errors are stored in self.error."""

        if data is None:
            self.error = 'No data.'
            return False

        try:
            start = data.index(b'$GPGGA')
            end = data.index(b'*', start)
        except ValueError:
            self.error = 'Sentence not found.'
            return False

        sentence = data[start+1:end]        # $ is not part of checksum
        checksum = int(data[end+1:end+3].decode('ascii'), 16)

        # Calculate checksum
        calculated = 0
        for b in sentence:
            calculated ^= b

        if checksum != calculated:
            self.error = 'Invalid checksum.'
            return False

        # Split and perform further checks
        self.nmea_segments = sentence.decode('ascii').split(',')

        if len(self.nmea_segments[1]) == 0:
            self.error = 'Time not synchronized.'
            return False

        if len(self.nmea_segments) < 10:
            self.error = 'Incomplete sentence.'
            return False

        # Retrieve all relevant data
        try:
            # UTC Timestamp
            utc_string = self.nmea_segments[1]
            self.timestamp = (int(utc_string[0:2]),
                              int(utc_string[2:4]),
                              int(utc_string[4:6]))

            # Type of fix
            self.fix_status = int(self.nmea_segments[6])

            # Satellite count
            self.satellites_in_use = int(self.nmea_segments[7])

            # Horizontal Dilution of Precision
            self.hdop = float(self.nmea_segments[8])

            if self.fix_status == 0:
                self.error = 'No fix obtained.'
                return False

            self.fix_time = utime.time()

            # Altitude
            self.altitude = float(self.nmea_segments[9])

            # Latitude
            lat = self.nmea_segments[2]
            lat_degs = float(lat[0:2])
            lat_mins = float(lat[2:])
            self.latitude = lat_degs + (lat_mins/60)
            if self.nmea_segments[3].lower() == 's':
                self.latitude *= -1

            # Longitude
            lon = self.nmea_segments[4]
            lon_degs = float(lon[0:3])
            lon_mins = float(lon[3:])
            self.longitude = lon_degs + (lon_mins/60)
            if self.nmea_segments[5].lower() == 'w':
                self.longitude *= -1

        except Exception as err:
            self.error = err
            return False
        else:
            self.error = None
            return True
