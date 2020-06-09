class Sensor:
    # Philips sensors can have the following values
    PRESENCE = None             # Boolean - Has presence been detected by the sensor?
    ON = None                   # Boolean - Is the sensor on?
    BATTERY = None              # Int - Level of battery (0-100)
    REACHABLE = None            # Boolean - Is the sensor reachable through the network/hub
    ALERT = None                # String - Alerts on the sensor (battery etc)
    SENSITIVITY = None          # Int - Sensitivity of the sensor to light and movement?
    LED = None                  # Boolean - Status of the LED
    TYPE = None                 # String - Type of the sensor
    MODEL_ID = None             # String - Model ID of the sensor (not unique)
    UNIQUE_ID = None            # String - Unique ID (like a MAC address)
    SW_VERSION = None           # String - Version of the sensors software
    PRODUCT_NAME = None         # String - Manufacturer given product name
