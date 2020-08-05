import time
import logging
import signal
from threading import Thread

# Defined by me
from utils.constants import *
from hub.config import *
from utils.logger import Logger
from hub.hub import Hub
from sensor.motion_sensor import MotionSensor
from light.light import Light

class Killer:
    kill = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill = True


def clean_up():
    """
        Gracefully shutdown by attempting to gracefully kill all our owned threads, and joining them before killing main
    """
    log.info("Shutting down gracefully...")

    if hub_heartbeat_thread.is_alive():
        hub.kill_thread()
        hub_heartbeat_thread.join()

    if hallway_motion_detected_thread.is_alive():
        hallway_motion_sensor.kill_thread()
        hallway_motion_detected_thread.join()

    # Set exit code to 0, to tell the runner that we ended cleanly
    exit(SUCCESS)


if __name__ == "__main__":
    system_state = RECOVERABLE
    log = None

    try:
        # Attempt to create a logger object so we can have some debug files!
        Logger.configure_log(__name__)
        log = Logger.get_logger()

        # Killer object that detects a SIGINT or SIGTERM
        killer = Killer()

        # Check that the logs were created before getting excited and initialising the system
        if log != ERROR:
            system_state = RUNNING
        else:
            raise RuntimeError("Failed creating logs...")

        # Grouping of the lights the hallway motion sensor controls
        HALLWAY_MOTION_SENSOR_LIGHTS = [Light(name=HUE_PLAY_TV, logger=log),
                                        Light(name=HUE_PLAY_BOOKCASE, logger=log),
                                        Light(name=LIVING_ROOM_LAMP, logger=log),
                                        Light(name=HALLWAY_SPOT_ONE, logger=log),
                                        Light(name=HALLWAY_SPOT_TWO, logger=log)]

        # Grouping of the lights the kitchen motion sensor controls
        KITCHEN_MOTION_SENSOR_LIGHTS = [Light(name=KITCHEN_COUNTER_SPOT, logger=log),
                                        Light(name=KITCHEN_SINK_SPOT, logger=log)]

        # Create the Hub and Motion Sensor objects we need, from the config file values
        hub = Hub(logger=log, found_at_ip=HUE_HUB_IP)
        hallway_motion_sensor = MotionSensor(logger=log, motion_sensor_name=HALLWAY_MOTION_SENSOR, connected_to_hub=hub, lights=HALLWAY_MOTION_SENSOR_LIGHTS)
        kitchen_motion_sensor = MotionSensor(logger=log, motion_sensor_name=KITCHEN_MOTION_SENSOR, connected_to_hub=hub, lights=KITCHEN_MOTION_SENSOR_LIGHTS)

        # Start a thread to ping the Hue hub, if these pings stop working, then perhaps the hub has gone down?
        hub_heartbeat_thread = Thread(name="hub_heartbeat_thread", target=hub.heartbeat)
        hub_heartbeat_thread.start()

        # Start a thread to constantly probe the hallway motion sensor for activity
        hallway_motion_detected_thread = Thread(name="hallway_motion_detected_thread", target=hallway_motion_sensor.interrogate)
        hallway_motion_detected_thread.start()

        # Start a thread to constantly probe the kitchen motion sensor for activity
        kitchen_motion_detected_thread = Thread(name="kitchen_motion_detected_thread", target=kitchen_motion_sensor.interrogate)
        kitchen_motion_detected_thread.start()

        # Allow the other threads to spawn
        time.sleep(10)

        # While a SIGINT or SIGTERM hasn't been received
        while not killer.kill:
            # If its recoverable then try to re launch it
            if hub.get_thread_state() == RECOVERABLE:
                # If its still alive then kill it
                if hub_heartbeat_thread.is_alive():
                    hub.kill_thread()
                    hub_heartbeat_thread.join()

                # Restart it
                hub_heartbeat_thread = Thread(name="hub_heartbeat_thread", target=hub.heartbeat)
                hub_heartbeat_thread.start()

            # If its recoverable then try to re launch it
            if hallway_motion_sensor.get_thread_state() == RECOVERABLE:
                # If its still alive then kill it
                if hallway_motion_detected_thread.is_alive():
                    hallway_motion_sensor.kill_thread()
                    hallway_motion_detected_thread.join()

                # Restart it
                hallway_motion_detected_thread = Thread(name="hallway_motion_detected_thread", target=hallway_motion_sensor.interrogate)
                hallway_motion_detected_thread.start()

            # If its recoverable then try to re launch it
            if kitchen_motion_sensor.get_thread_state() == RECOVERABLE:
                # If its still alive then kill it
                if kitchen_motion_detected_thread.is_alive():
                    kitchen_motion_sensor.kill_thread()
                    kitchen_motion_detected_thread.join()

                # Restart it
                kitchen_motion_detected_thread = Thread(name="kitchen_motion_detected_thread", target=kitchen_motion_sensor.interrogate)
                kitchen_motion_detected_thread.start()

            time.sleep(10)

        # Join the threads, so we don't end up trashing them forcefully
        clean_up()

    except Exception as e:
        if log is not None and log != ERROR:
            log.exception(e)
            logging.shutdown()
            exit(ERROR)
        else:
            print(e)

    logging.shutdown()
    exit(SUCCESS)
