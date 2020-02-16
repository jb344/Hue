import json


def command(power: bool, brightness: int = None, hue: int = None, saturation: int = None, effect: str = None, xy: list = None, colour_mode: str = None):
    cmd = {"on": power}

    if brightness:
        cmd["bri"] = brightness
    if hue:
        cmd["hue"] = hue
    if saturation:
        cmd["saturation"] = saturation
    if effect:
        cmd["effect"] = effect
    if xy:
        cmd["xy"] = xy
    if colour_mode:
        cmd["colormode"] = colour_mode

    return cmd
