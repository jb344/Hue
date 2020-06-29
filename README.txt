This code is designed to enhance the usability of your Philips Hue system, by improving the capability of the Hue Motion Sensor.

The official app only supports two different times of day where the motion sensor can trigger different colour/temperatures of light. This code enhances that by adding completely customisable activity at any time of day, although some alteration to the existing code will be necessary.

Alongside this it also prevents the motion sensor from overriding current light settings/state when the sensor is triggered. For example if you have set your lounge to "relax", but somebody triggers the hallway requiring bright white, the code will recognise the light as already being in a separate state and therefore will not override or disturb the current state/scene. Allowing you to enjoy the temperature/colour you assigned.

The code can be deployed from any platform with network access to the Hue bridge. I run this from a Raspberry Pi 2 as a systemctl service.

Incorporated within is seasonal information (so it recognises days are longer in the summer), however this is configured for the northern hemisphere; changes will need to be made to utils->constants.py to alter this behaviour.

No additional libraries are needed. The code just simply requires Python 3

To get started;

1. Setup a privileged Hue Hub user using this method; https://developers.meethue.com/develop/get-started-2/
2. Check your Hue Hub IP address (default is 192.168.1.27) and change the HUE_HUB_IP field in hub->config.py
3. Adjust LOGGING_PATH in utils->constants.py
4. Update the months depending on your hemisphere in utils->constants.py
5. Run using "python3 main.py"
