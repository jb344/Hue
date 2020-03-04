import json
import urllib.request
import threading
from time import sleep

# Defined by me
from urllib.error import URLError

from hub.config import *
from utils.constants import *
from hub.hub import Hub
from sensor.sensor import Sensor
from light.light import Light
from utils.time import get_current_time


class MotionSensor(Sensor):
    def __init__(self, logger, motion_sensor_name: str, connected_to_hub: Hub):
        """
            Constructor of a MotionSensor, which inherits from a Sensor
                :param logger:                  Logger to log to
                :param motion_sensor_name:      Name of the motion sensor we are interested in
                :param connected_to_hub:        hub.Hub class object that the desired MotionSensor is connected to
        """
        self.LOGGER = logger                            # Logger object
        self.THREAD_STATE = RECOVERABLE                 # State flag of this thread, either RUNNING, RECOVERABLE, or IRRECOVERABLE
        self.THREAD_STATE_MUTEX = threading.Lock()      # Mutex protecting the above flag
        self.MOTION_SENSOR_NAME = motion_sensor_name    # Name of the motion sensor we are looking to interrogate
        self.HUB = connected_to_hub                     # The Hue hub object that the sensor is connected to

        # Lounge lights
        self.HUE_PLAY = Light(name=HUE_PLAY, logger=logger)
        self.LOUNGE_LAMP = Light(name=LIVING_ROOM_LAMP, logger=logger)
        self.ALL_LOUNGE_LIGHTS = [self.HUE_PLAY, self.LOUNGE_LAMP]

        # Hallway lights
        self.HALLWAY_SPOT_ONE = Light(name=HALLWAY_SPOT_ONE, logger=logger)
        self.HALLWAY_SPOT_TWO = Light(name=HALLWAY_SPOT_TWO, logger=logger)
        self.ALL_HALLWAY_LIGHTS = [self.HALLWAY_SPOT_ONE, self.HALLWAY_SPOT_TWO]

        # Bedroom lights
        self.BEDROOM_LAMP = Light(name=BEDROOM_LAMP, logger=logger)
        self.ALL_BEDROOM_LIGHTS = []

    def interrogate(self) -> int:
        """
            Get state information from the sensor
                :return:            -1 on FAILURE, 0 on SUCCESS
        """
        try:
            self.set_thread_state(RUNNING)
            self.LOGGER.info("Motion sensor interrogation thread started on {}".format(self.MOTION_SENSOR_NAME))

            # Keep this thread running if the Hub is still alive, and main hasn't told this thread to stop
            while self.get_thread_state() != KILL:
                try:
                    # Send a HTTP GET request to the hub from information about all the sensors
                    http_result = urllib.request.urlopen(HUE_HUB_BASE_URL + SENSORS_URL).read()

                    if http_result is not None:
                        # The hub returns JSON, so we pass in a decoded byte array, so a string, to the JSON library
                        json_result = json.loads(http_result.decode())

                        # Iterate over all the sensors until we find the motion sensor we are looking for
                        for sensor_id, sensor_fields in json_result.items():
                            if self.MOTION_SENSOR_NAME in sensor_fields.get("name"):
                                # Get state information, and whether the sensor has detected anything
                                sensor_state = sensor_fields.get("state")
                                self.PRESENCE = sensor_state.get("presence")

                                # Get the current time, so if it's 3AM we get the rest of the sensor information, rather doing it every iteration
                                # and slowing the code down
                                hour, minute, *_ = get_current_time(self.LOGGER)

                                # If its 3AM then probe the rest of the details from the sensor
                                if hour == 3 and minute == 0:
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

                                    self.LOGGER.debug("Motion sensor state;\n"
                                                      "\t\t\t\t\t\tpresence    {}\n".format(self.PRESENCE) +
                                                      "\t\t\t\t\t\ton          {}\n".format(self.ON) +
                                                      "\t\t\t\t\t\tbattery     {}\n".format(self.BATTERY) +
                                                      "\t\t\t\t\t\treachable   {}\n".format(self.REACHABLE) +
                                                      "\t\t\t\t\t\talert       {}\n".format(self.ALERT) +
                                                      "\t\t\t\t\t\tsensitivity {}\n".format(self.SENSITIVITY) +
                                                      "\t\t\t\t\t\tuid         {}".format(self.UNIQUE_ID))

                                break

                        # If presence is detected then attempt to switch on all the necessary lights if they aren't already
                        if self.PRESENCE:
                            # Iterate over the bedroom lights and if they aren't on, switch them on
                            for each_light in self.ALL_BEDROOM_LIGHTS:
                                each_light.switch_on()

                            # Iterate over the lounge lights and if they aren't on, switch them on
                            for each_light in self.ALL_LOUNGE_LIGHTS:
                                each_light.switch_on()

                            # Iterate over the hallway lights and if they aren't on, switch them on
                            for each_light in self.ALL_HALLWAY_LIGHTS:
                                each_light.switch_on()

                    # 100Hz refresh rate
                    sleep(0.01)
                except URLError as err:
                    # Catch a 101 (Network is unreachable) and 113 (No route to host), because every night at 2AM the network goes down
                    if URLError.errno == 101 or URLError.errno == 113:
                        sleep(60)
                        continue
                    else:
                        raise OSError(err)

            return SUCCESS
        except Exception as err:
            self.LOGGER.exception(err)
            self.set_thread_state(RECOVERABLE)
            return ERROR

    def set_thread_state(self, state: int):
        """
            Set the state of this thread in a thread-safe manner
                :param state:           State to set the thread to
                :return:                -1 on FAILURE, 0 on SUCCESS
        """
        with self.THREAD_STATE_MUTEX:
            self.THREAD_STATE = state

        return SUCCESS

    def get_thread_state(self):
        """
            Get the state of this thread
                :return:                Thread state, either RUNNING, RECOVERABLE, or IRRECOVERABLE
        """
        with self.THREAD_STATE_MUTEX:
            return self.THREAD_STATE

    def kill_thread(self):
        """
            Kill the thread
        """
        self.set_thread_state(KILL)
