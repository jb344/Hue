import json
import urllib.request

# Defined by me
from hub.config import *
from light.command import command


class LightState:
    def __init__(self, light_name=None, state_json=None, construct_from_json=False):
        light_state = None

        if construct_from_json is False and light_name is not None:
            # Get state information from every light, the returned JSON is structured like in example_state_information.json
            # Send a HTTP GET request to the hub from information about all the sensors
            http_result = urllib.request.urlopen(HUE_HUB_BASE_URL + LIGHTS_URL).read()
            # The hub returns JSON, so we pass in a decoded byte array, so a string, to the JSON library
            json_result = json.loads(http_result.decode())

            # Iterate over all the sensors until we find the motion sensor we are looking for
            for light_id, light_fields in json_result.items():
                if light_name in light_fields.get("name"):
                    # Get state information
                    light_state = light_fields.get("state")
                    break
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

    def to_json(self):
        return command(self.ON, self.BRIGHTNESS, self.HUE, self.SATURATION, self.EFFECT, self.XY, self.COLOUR_MODE)

    def __eq__(self, other):
        # For now just compare "on", "bri" and "ct", as these fields are common between full colour lights, ambiance only etc...
        if self.ON == other.ON and self.BRIGHTNESS == other.BRIGHTNESS and self.CT == other.CT:
            return True
        else:
            return False
