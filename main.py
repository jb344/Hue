import time
import logging
from threading import Thread

# Defined by me
from utils.constants import *
from hub.config import *
from utils.logger import Logger
from hub.hub import Hub
from sensor.motion_sensor import MotionSensor


def terminate():
    """
        Gracefully shutdown by attempting to gracefully kill all our owned threads, and joining them before killing main
    """
    if hub_heartbeat_thread.is_alive():
        hub.kill_thread()
        hub_heartbeat_thread.join()

    if motion_detected_thread.is_alive():
        motion_sensor.kill_thread()
        motion_detected_thread.join()

    # Set exit code to 0, to tell the runner that we ended cleanly
    exit(0)


if __name__ == "__main__":
    system_state = RECOVERABLE
    log = None

    try:
        # Attempt to create a logger object so we can have some debug files!
        Logger.configure_log(__name__)
        log = Logger.get_logger()

        # Check that the logs were created before getting excited and initialising the system
        if log != ERROR:
            system_state = RUNNING
        else:
            raise RuntimeError("Failed creating logs...")

        # Create the Hub and Motion Sensor objects we need, from the config file values
        hub = Hub(logger=log, found_at_ip=HUE_HUB_IP)
        motion_sensor = MotionSensor(logger=log, motion_sensor_name=MOTION_SENSOR_NAME, connected_to_hub=hub)

        # Start a thread to ping the Hue hub, if these pings stop working, then perhaps the hub has gone down?
        hub_heartbeat_thread = Thread(name="hub_heartbeat_thread", target=hub.heartbeat)
        hub_heartbeat_thread.start()

        # Start a thread to constantly probe the motion sensor for activity
        motion_detected_thread = Thread(name="motion_detected_thread", target=motion_sensor.interrogate)
        motion_detected_thread.start()

        # Wait for the threads to both hit the RUNNING state
        while hub.get_thread_state() != RUNNING and motion_sensor.get_thread_state() != RUNNING:
            time.sleep(1)

        while system_state == RUNNING:
            system_state = hub.get_thread_state() | motion_sensor.get_thread_state()
            time.sleep(10)

        # Join the threads, so we don't end up trashing them forcefully
        terminate()

    except Exception as e:
        if log is not None and log != ERROR:
            log.exception(e)
            logging.shutdown()
            exit(ERROR)
        else:
            print(e)

    logging.shutdown()
    exit(SUCCESS)
