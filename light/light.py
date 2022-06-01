import json
import urllib.request
from datetime import datetime
from datetime import timedelta
import threading
from threading import Thread
from time import sleep

# Defined by me
from hub.config import *
from light.state import LightState
from utils.time import *


class Light:
    def __init__(self, name, logger):
        """
            Constructor
                :param name:        Name of the light to get, such as "Living room lamp"
                :param logger:      Logger to log to
        """
        self.DAY_OF_WEEK = None                     # Current day of the week (e.g. Monday = 1)
        self.DAYTIME_HOUR = None                    # Hour which daytime starts
        self.NIGHT_HOUR = None                      # Hour which night starts
        self.EVENING_HOUR = None                    # Hour which evening starts
        self.CURRENT_STATE = None                   # LightState class object, containing the current state of the light
        self.INITIAL_STATE = None                   # LightState class object, containing the state of the light as we "found" it, so we can return to this if necessary
        self.MODIFIED_STATE = None                  # LightState class object, containing the state of the light as we have set it
        self.ID = None                              # ID of the light stored in the Hub (0+)
        self.TYPE = None                            # String - Type of the light (full colour, ambient and white only, etc...)
        self.NAME = name                            # String - Name of the light (set by me)
        self.MODEL_ID = None                        # String - Model ID of the sensor (not unique)
        self.UNIQUE_ID = None                       # String - Unique ID (like a MAC address)
        self.SW_VERSION = None                      # String - Version of the sensors software
        self.PRODUCT_NAME = None                    # String - Manufacturer given product name
        self.LOGGER = logger                        # Logger object
        self.LAST_ON_TIME = None                    # Time at which the light was last turned on
        self.RESET_THREAD = None                    # Thread object for resetting the light to its previous state
        self.RESET_TIME = None                      # Datetime object which contains the system time at which this light should switch off/return to previous state
        self.RESET_TIME_MUTEX = threading.Lock()    # Mutex protecting the variable above, so if the sensor is triggered again within the "stay on"

        # Get state information from every light, the returned JSON is structured like in example_state_information.json
        # Send a HTTP GET request to the hub from information about all the sensors
        http_result = urllib.request.urlopen(url=HUE_HUB_BASE_URL + LIGHTS_URL).read()
        # The hub returns JSON, so we pass in a decoded byte array, so a string, to the JSON library
        json_result = json.loads(http_result.decode())

        # Iterate over all the lights until we find the one we want
        for light_id, light_fields in json_result.items():
            if self.NAME in light_fields.get("name"):
                # Get the current state information so we can return to this after a defined time interval
                self.INITIAL_STATE = LightState(logger=self.LOGGER, light_name=self.NAME)

                # Get generic information
                self.ID = light_id
                self.TYPE = light_fields.get("type")
                self.MODEL_ID = light_fields.get("modelid")
                self.PRODUCT_NAME = light_fields.get("productname")
                self.SW_VERSION = light_fields.get("swversion")
                self.UNIQUE_ID = light_fields.get("uniqueid")

                break

    def switch_on(self) -> int:
        """
            Send the HTTP PUT request to the Hue hub in order to switch on the physical light represented by this Light object
                :return:        -1 on FAILURE, 0 on SUCCESS
        """
        try:
            # What day of the week is it
            self.DAY_OF_WEEK = get_current_weekday()

            # If its the day of week that we want to check the season, or we haven't checked yet
            if self.DAY_OF_WEEK == DAY_OF_WEEK_TO_CHECK_SEASON or self.DAYTIME_HOUR is None:
                # Set the light boundaries, we should probably only do this on a weekly basis
                self.set_light_colour_time_boundaries()

            # Get the current state information so we can return to this after a defined time interval
            self.CURRENT_STATE = LightState(logger=self.LOGGER, light_name=self.NAME)

            # If the light isn't currently on, then attempt to turn it on
            if not self.CURRENT_STATE.ON:
                self.INITIAL_STATE = self.CURRENT_STATE

                # Based on the current time, decide which colour we want the lights
                hour = get_current_hour()

                # At night we want a dimmed light
                if hour in self.NIGHT_HOUR:
                    with open("/home/pi/Hue/light/json/dimmed.json") as f:
                        on_command = json.load(f)
                # In the day time we want bright light - do nothing for now
                elif hour in self.DAYTIME_HOUR:
                    # with open("/home/pi/Hue/light/json/energise.json") as f:
                    #     on_command = json.load(f)
                    # Do nothing during daytime for now
                    return SUCCESS
                # In the evening we want a relaxed colour
                elif hour in self.EVENING_HOUR:
                    with open("/home/pi/Hue/light/json/relaxed.json") as f:
                        on_command = json.load(f)

                # Store the state that we just set this() light to
                self.MODIFIED_STATE = LightState(logger=self.LOGGER, state_json=on_command, construct_from_json=True)

                # URL of this() light
                resource_url = HUE_HUB_BASE_URL + LIGHTS_URL + "/" + self.ID + STATE_URL

                # Switch this() light on
                self.LOGGER.debug("Switching {} on, using command {}".format(self.NAME, on_command))
                http_result = urllib.request.urlopen(url=urllib.request.Request(url=resource_url, method='PUT', data=json.dumps(on_command).encode())).read()

                # Check the returned json confirms success on our request
                if "success" in http_result.decode():
                    self.LAST_ON_TIME = datetime.datetime.now()
                    self.set_reset_time(self.LAST_ON_TIME)

                    # If we haven't already got a reset thread running for this() light, then start one, so after hub.config.STAY_ON_FOR_X_MINUTES minutes this() light will be reset
                    if self.RESET_THREAD is None:
                        self.RESET_THREAD = Thread(name="LIGHT_RESET_THREAD", target=self.reset_light)
                        self.RESET_THREAD.start()
                        self.LOGGER.info("{} was switched on at {}, reverting to previous state at {}, thread handling this {}".format(self.NAME, self.LAST_ON_TIME, self.get_reset_time(), self.RESET_THREAD.getName()))
                    return SUCCESS
                else:
                    raise RuntimeError("Error switching on light using command {}".format(on_command))
            else:
                # The light is currently switched on, and we have triggered the motion sensor, so check if a reset thread exists for the light, if it does then extend the reset time
                if self.RESET_THREAD is not None:
                    self.set_reset_time(datetime.datetime.now())
                    self.LOGGER.info("{} was already switched on at {} when the motion sensor was re-triggered, extending the reversion to previous state by {} minutes - "
                                     "reverting to previous state at {}, thread handling this {}".format(self.NAME, self.LAST_ON_TIME, STAY_ON_FOR_X_MINUTES, self.get_reset_time(), self.RESET_THREAD.getName()))
        except Exception as err:
            self.LOGGER.exception(err)
            return ERROR

    def reset_light(self) -> int:
        """
            This function runs in its own thread, and switches off this() light after STAY_ON_FOR_X_MINUTES time has passed since switching it on.
            It calculates the time delta in a loop, and when the delta is zero it sends a HTTP PUT request to the Hue hub to reset this() light, dependant on its
            current state
                :return:        -1 on FAILURE, 0 on SUCCESS
        """
        try:
            # While the current time is less than that we need to reset this() light at, then we should sleep and wait for it to be True
            delta = self.get_reset_time() - datetime.datetime.now()
            while delta.seconds > 0:
                delta = self.get_reset_time() - datetime.datetime.now()
                sleep(1)

            # Get the current state information so we can make a guess at whether it was the motion sensor that recently changed the status, or whether it was something else,
            # if it was something else, then we probably don't want to go about resetting the lights
            self.CURRENT_STATE = LightState(logger=self.LOGGER, light_name=self.NAME)

            # If this() light is in the same state to the one that we changed it to, then reset back to initial;
            # Initial(OFF)      ->      Modified(RED)       ->      Current(RED)        ->      RESET TO INITIAL
            if self.MODIFIED_STATE == self.CURRENT_STATE:
                resource_url = HUE_HUB_BASE_URL + LIGHTS_URL + "/" + self.ID + STATE_URL
                # Return to the previous state
                http_result = urllib.request.urlopen(url=urllib.request.Request(url=resource_url, method='PUT'),
                                                     data=json.dumps(self.INITIAL_STATE.to_json()).encode()).read()

                if "success" in http_result.decode():
                    self.LOGGER.debug("{} was returned to its initial state {}".format(self.NAME, self.INITIAL_STATE.to_json()))
                else:
                    raise RuntimeError("Error returning light {} to its initial state {}".format(self.NAME, self.INITIAL_STATE.to_json()))
            elif not self.CURRENT_STATE == self.MODIFIED_STATE and not self.CURRENT_STATE == self.INITIAL_STATE:
                # If the light is in a different state to both initial and the modified, then a third party has overridden the state we generated, so do nothing;
                # Initial(OFF)      ->      Modified(RED)       ->      Current(BLUE)        ->     DO NOTHING
                self.LOGGER.debug("{} does not need any further action, as a third party has changed the state of the light since we have, thus overriding our setting".format(self.NAME))
            elif self.CURRENT_STATE == self.INITIAL_STATE:
                # If the light has already been put back to its initial state by a third party, then do nothing;
                # Initial(OFF)      ->      Modified(RED)       ->      Current(OFF)        ->     DO NOTHING
                self.LOGGER.debug("{} does not need any further action, as a third has put the light back to its initial state, so we don't have to".format(self.NAME))

            # Reset back to None to indicate there is no thread running anymore, and one should be created if needed
            self.RESET_THREAD = None
            return SUCCESS
        except Exception as err:
            self.LOGGER.exception(err)
            # Reset back to None to indicate there is no thread running anymore, and one should be created if needed
            self.RESET_THREAD = None
            return ERROR

    def get_reset_time(self) -> datetime:
        """
            Get the datetime object in a thread-safe manner, detailing when reset behaviour should be run
                :return:        datetime object telling us the reset time
        """
        with self.RESET_TIME_MUTEX:
            return self.RESET_TIME

    def set_reset_time(self, current_time: datetime):
        """
            Set the reset time of this() light
                :param current_time:        Current time that we should calculate the reset time from
        """
        with self.RESET_TIME_MUTEX:
            self.RESET_TIME = current_time + timedelta(minutes=STAY_ON_FOR_X_MINUTES)

    def set_light_colour_time_boundaries(self) -> int:
        """
            Determine the boundaries of what colour light we want at what time
            dependant on the current season/month
                :return:        -1 on FAILURE, 0 on SUCCESS
        """
        # Get the current month of the year
        month = get_current_month()

        # Winter has the shortest daylight hours...
        if month in WINTER_MONTHS:
            self.DAYTIME_HOUR = [8, 9, 10, 11, 12, 13, 14, 15, 16]
            self.EVENING_HOUR = [17, 18, 19, 20, 21, 22]
            self.NIGHT_HOUR = [23, 0, 1, 2, 3, 4, 5, 6, 7]
        elif month in SPRING_MONTHS:
            self.DAYTIME_HOUR = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
            self.EVENING_HOUR = [19, 20, 21]
            self.NIGHT_HOUR = [22, 23, 0, 1, 2, 3, 4, 5]
        # Summer has the longest daylight hours...
        elif month in SUMMER_MONTHS:
            self.DAYTIME_HOUR = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
            self.EVENING_HOUR = [20, 21, 22]
            self.NIGHT_HOUR = [23, 0, 1, 2, 3]
        elif month in AUTUMN_MONTHS:
            self.DAYTIME_HOUR = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            self.EVENING_HOUR = [18, 19, 20, 21]
            self.NIGHT_HOUR = [22, 23, 0, 1, 2, 3, 4]

        return SUCCESS
