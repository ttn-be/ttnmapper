from network import WLAN

##### Settings for WLAN STA mode #####

WLAN_MODE         = 'ap'
#WLAN_SSID         = ''
#WLAN_AUTH         = (WLAN.WPA2,'')

##### LoRaWAN Configuration #####

LORA_ENABLE       = False
LORA_ENABLE_PIN   = 'P9'
LORA_APP_EUI      = '70B3D57EF0001ED4'
LORA_APP_KEY      = None      # See README.md for instructions!

# Interval between measures transmitted to TTN.
# Measured airtime of transmission is 56.6 ms, fair use policy limits us to
# 30 seconds per day (= roughly 500 messages). We default to a 180 second
# interval (=480 messages / day).
LORA_SEND_RATE    = 180

##### GNSS Configuration #####

GNSS_TIMEOUT      = 5000      # Timeout for obtaining position (miliseconds)
GNSS_ENABLE_PIN   = 'P8'
GNSS_UART_PORT    = 1
GNSS_UART_BAUD    = 9600
