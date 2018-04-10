from network import WLAN

###############################################################################
# Settings for WLAN STA mode
###############################################################################

WLAN_MODE         = 'off'
#WLAN_SSID         = ''
#WLAN_AUTH         = (WLAN.WPA2,'')

###############################################################################
# LoRaWAN Configuration
###############################################################################

# May be either 'otaa', 'abp', or 'off'
LORA_MODE         = 'otaa'

# Settings for mode 'otaa'
LORA_OTAA_EUI     = '70B3D57EF0001ED4'
LORA_OTAA_KEY     = None      # See README.md for instructions!

# Settings for mode 'abp'
#LORA_ABP_DEVADDR  = ''
#LORA_ABP_NETKEY   = ''
#LORA_ABP_APPKEY   = ''

# Interval between measures transmitted to TTN.
# Measured airtime of transmission is 56.6 ms, fair use policy limits us to
# 30 seconds per day (= roughly 500 messages). We default to a 180 second
# interval (=480 messages / day).
LORA_SEND_RATE    = 180

###############################################################################
# GNSS Configuration
###############################################################################

GNSS_UART_PORT    = 1
GNSS_UART_BAUD    = 9600
GNSS_ENABLE_PIN   = 'P8'
