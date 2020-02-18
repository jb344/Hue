import json
import urllib.request

# Defined by me
from hub.config import *
from utils.constants import *
from light.command import command


class LightState:
    def __init__(self, logger, light_name=None, state_json=None, construct_from_json=False):
        """
            Constructor
                :param logger:                      Logger object to log to
                :param light_name:                  Name of the light that this LightState object stores information for
                :param state_json:                  A json structure to build a LightState from
                :param construct_from_json:         Flag to determine whether we build a LightState from state_json or from performing a HTTP GET on a light reosurce defined by light_name
        """
        light_state = None

        try:
            self.LOGGER = logger

            # Construct from a HTTP GET request sent to the Hue Hub
            if construct_from_json is False and light_name is not None:
                # Send a HTTP GET request to the hub for state information about all the lights
                http_result = urllib.request.urlopen(HUE_HUB_BASE_URL + LIGHTS_URL).read()
                # The hub returns JSON, so we pass in a decoded byte array, so a string, to the JSON library
                json_result = json.loads(http_result.decode())

                # Iterate over all the lights until we find the one we are looking for
                for light_id, light_fields in json_result.items():
                    if light_name in light_fields.get("name"):
                        # Get state information
                        light_state = light_fields.get("state")
                        break

            # Construct from some pre-defined json
            elif construct_from_json is True and state_json is not None:
                light_state = state_json

            if light_state is not None:
                self.NAME = light_name                              # Name of the light
                self.ON = light_state.get("on")                     # Boolean - Is the light on?
                self.BRIGHTNESS = light_state.get("bri")            # Int - Level of brightness (0-255)
                self.HUE = light_state.get("hue")                   # Int - Level of hue
                self.SATURATION = light_state.get("sat")            # Int - Level of saturation
                self.EFFECT = light_state.get("effect")             # String - colorloop, etc...
                self.XY = light_state.get("xy")                     # Float[] - TODO
                self.CT = light_state.get("ct")                     # Int - Colour temperature
                self.COLOUR_MODE = light_state.get("colormode")     # String - Either xy, ct, etc...
                self.REACHABLE = light_state.get("reachable")       # Boolean - Is the light reachable through the network/hub
                self.ALERT = light_state.get("alert")               # String - Alerts on the light
            else:
                raise ValueError("Unable to construct a LightState object, light_state is None")
        except Exception as err:
            self.LOGGER.exception(err)

    def to_json(self) -> dict or int:
        """
            Convert this LightState object into a dict/json representation for sending over HTTP PUT to the Hue hub
                :return:        dict containing this LightState, or -1 on FAILURE
        """
        try:
            return command(self.ON, self.BRIGHTNESS, self.HUE, self.SATURATION, self.EFFECT, self.XY, self.COLOUR_MODE)
        except Exception as err:
            self.LOGGER.exception(err)
            return ERROR

    def __eq__(self, other) -> bool:
        """
            Determine whether two LightState objects are equal by comparing their ON, BRIGHTNESS and CT (Colour Temperature) fields
                :param other:       The other LightState object to compare with
                :return:            True if they're equal, False otherwise
        """
        # For now just compare "on", "bri" and "ct", as these fields are common between full colour lights, ambiance only etc...
        if self.ON == other.ON and self.BRIGHTNESS == other.BRIGHTNESS and self.CT == other.CT:
            return True
        else:
            return False
