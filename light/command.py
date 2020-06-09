def command(power: bool, brightness: int = None, hue: int = None, saturation: int = None, effect: str = None, xy: list = None, ct: int = None, colour_mode: str = None) -> dict:
    """
        Create a dictionary which has the structure/fields of a Philips Hue light, so we can then translate this dictionary into json, and use a HTTP PUT
        request to send it to the hub
            :param power:               Power state of something connected to the Hue hub (true or false)
            :param brightness:          Brightness
            :param hue:                 Hue
            :param saturation:          Saturation
            :param effect:              Effect - colorloop etc...
            :param xy:
            :param ct:                  Colour temperature
            :param colour_mode:         Mode - ct (Colour temperature), xy (defined by the field above) etc...
            :return:                    Dictionary
    """
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
    if ct:
        cmd["ct"] = ct
    if colour_mode:
        cmd["colormode"] = colour_mode

    return cmd
