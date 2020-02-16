import json
import urllib.request

# Defined by me
from hub.config import *
from utils.constants import *


class Light:
    def __init__(self, name, logger):
        """
            Constructor
                :param name:        Name of the light to get, such as "Living room lamp"
        """
        self.ON = None                  # Boolean - Is the light on?
        self.BRIGHTNESS = None          # Int - Level of brightness (0-255)
        self.HUE = None                 # Int - Level of hue
        self.SATURATION = None          # Int - Level of saturation
        self.EFFECT = None              # String - TODO
        self.XY = None                  # Float[] - TODO
        self.COLOUR_MODE = None         # String - TODO
        self.REACHABLE = None           # Boolean - Is the light reachable through the network/hub
        self.ALERT = None               # String - Alerts on the light
        self.TYPE = None                # String - Type of the light (full colour, ambient and white only, etc...)
        self.NAME = None                # String - Name of the light (set by me)
        self.MODEL_ID = None            # String - Model ID of the sensor (not unique)
        self.UNIQUE_ID = None           # String - Unique ID (like a MAC address) TODO check what kind of ID this is
        self.SW_VERSION = None          # String - Version of the sensors software
        self.PRODUCT_NAME = None        # String - Manufacturer given product name
        self.LOGGER = logger            # Logger object

        # Get the state of the desired light
        self.get_state(name)

    def get_state(self, name):
        """
            Get state information from every light, the returned JSON looks like the following;
                "1": {
                    "state": {
                        "on": true,
                        "bri": 254,
                        "hue": 41442,
                        "sat": 75,
                        "effect": "none",
                        "xy": [
                            0.3146,
                            0.3303
                        ],
                        "ct": 156,
                        "alert": "none",
                        "colormode": "xy",
                        "mode": "homeautomation",
                        "reachable": true
                    },
                    "swupdate": {
                        "state": "noupdates",
                        "lastinstall": "2020-02-05T14:49:23"
                    },
                    "type": "Extended color light",
                    "name": "Living room lamp",
                    "modelid": "LCA001",
                    "manufacturername": "Philips",
                    "productname": "Hue color lamp",
                    "capabilities": {
                        "certified": true,
                        "control": {
                            "mindimlevel": 200,
                            "maxlumen": 800,
                            "colorgamuttype": "C",
                            "colorgamut": [
                                [
                                    0.6915,
                                    0.3083
                                ],
                                [
                                    0.17,
                                    0.7
                                ],
                                [
                                    0.1532,
                                    0.0475
                                ]
                            ],
                            "ct": {
                                "min": 153,
                                "max": 500
                            }
                        },
                        "streaming": {
                            "renderer": true,
                            "proxy": true
                        }
                    },light_fields.get("name")
                    "config": {
                        "archetype": "sultanbulb",
                        "function": "mixed",
                        "direction": "omnidirectional",
                        "startup": {
                            "mode": "safety",
                            "configured": true
                        }
                    },
                    "uniqueid": "00:17:88:01:08:31:d0:93-0b",
                    "swversion": "1.65.9_hB3217DF",
                    "swconfigid": "BD38721C",
                    "productid": "Philips-LCA001-5-A19ECLv6"
                },

                :param name:        Name of the light to get the state of
        """
        # Send a HTTP GET request to the hub from information about all the sensors
        http_result = urllib.request.urlopen(HUE_HUB_BASE_URL + SENSORS_URL).read()
        # The hub returns JSON, so we pass in a decoded byte array, so a string, to the JSON library
        json_result = json.loads(http_result.decode())

        # Iterate over all the sensors until we find the motion sensor we are looking for
        for light_id, light_fields in json_result.items():
            if name in light_fields.get("name"):
                # Get state information
                light_state = light_fields.get("state")
                self.ON = light_state.get("on")
                self.BRIGHTNESS = light_state.get("bri")
                self.HUE = light_state.get("hue")
                self.SATURATION = light_state.get("sat")
                self.EFFECT = light_state.get("effect")
                self.XY = light_state.get("xy")
                self.COLOUR_MODE = light_state.get("colormode")
                self.REACHABLE = light_state.get("reachable")
                self.ALERT = light_state.get("alert")

                # Get generic information
                self.TYPE = light_fields.get("type")
                self.NAME = name
                self.MODEL_ID = light_fields.get("modelid")
                self.PRODUCT_NAME = light_fields.get("productname")
                self.SW_VERSION = light_fields.get("swversion")
                self.UNIQUE_ID = light_fields.get("uniqueid")

                break

        return SUCCESS
