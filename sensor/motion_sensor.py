import json
import urllib.request
from collections import namedtuple

# Defined by me
from hub.config import *
from utils.constants import *


class MotionSensor:
    def __init__(self, log=None):
        self.PRESENCE = None            # Boolean - Has presence been detected by the sensor?
        self.ON = None                  # Boolean - Is the sensor on?
        self.BATTERY = None             # Int - Level of battery (0-100)
        self.REACHABLE = None           # Boolean - Is the sensor reachable through the network/hub
        self.ALERT = None               # String - Alerts on the sensor (battery etc)
        self.SENSITIVITY = None         # Int - Sensitivity of the sensor to light and movement? TODO check docs
        self.LED = None                 # Boolean - Status of the LED
        self.TYPE = None                # String - Type of the sensor TODO check docs for different types
        self.MODEL_ID = None            # String - Model ID of the sensor (not unique)
        self.UNIQUE_ID = None           # String - Unique ID (like a MAC address) TODO check what kind of ID this is
        self.SW_VERSION = None          # String - Version of the sensors software
        self.PRODUCT_NAME = None        # String - Manufacturer given product name
        self.LOGGER = log               # Logger object

    def get_state(self):
        try:
            """
                Get state information from the sensor, the returned JSON looks like the following;
                    {
                        "state": {
                            "presence": false,
                            "lastupdated": "2020-02-13T19:41:25"
                        },
                        "swupdate": {
                            "state": "noupdates",
                            "lastinstall": "2020-02-08T09:51:00"
                        },
                        "config": {
                            "on": true,
                            "battery": 100,
                            "reachable": true,
                            "alert": "none",
                            "sensitivity": 2,
                            "sensitivitymax": 2,
                            "ledindication": false,
                            "usertest": false,
                            "pending": []
                        },
                        "name": "Hallway motion sensor",
                        "type": "ZLLPresence",
                        "modelid": "SML001",
                        "manufacturername": "Philips",
                        "productname": "Hue motion sensor",
                        "swversion": "6.1.1.27575",
                        "uniqueid": "00:17:88:01:06:f7:31:91-02-0406",
                        "capabilities": {
                            "certified": true,
                            "primary": true
                        }
                    }
            """
            # Send a HTTP GET request to the hub from information about all the sensors
            http_result = urllib.request.urlopen(HUE_HUB_BASE_URL + SENSORS_URL).read()
            # The hub returns JSON, so we pass in a decoded byte array, so a string, to the JSON library
            json_result = json.loads(http_result.decode())

            # Iterate over all the sensors until we find the motion sensor we are looking for
            for sensor_id, sensor_fields in json_result.items():
                if MOTION_SENSOR_NAME in sensor_fields.get("name"):
                    # Get state information
                    sensor_state = sensor_fields.get("state")
                    self.PRESENCE = sensor_state.get("presence")

                    # Get configuration information
                    sensor_config = sensor_fields.get("config")
                    self.ON = sensor_config.get("on")
                    self.BATTERY = sensor_config.get("battery")
                    self.REACHABLE = sensor_config.get("reachable")
                    self.ALERT = sensor_config.get("alert")
                    self.SENSITIVITY = sensor_config.get("sensitivity")
                    self.LED = sensor_config.get("ledindication")

                    # Get generic information
                    self.TYPE = sensor_fields.get("type")
                    self.MODEL_ID = sensor_fields.get("modelid")
                    self.PRODUCT_NAME = sensor_fields.get("productname")
                    self.SW_VERSION = sensor_fields.get("swversion")
                    self.UNIQUE_ID = sensor_fields.get("uniqueid")

                    break

            if self.PRESENCE:
                # Get light states
                i = 0
        except Exception as err:
            self.LOGGER.exception(err)
            return ERROR
