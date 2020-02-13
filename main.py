import time
import logging
from threading import Thread

# Defined by me
from utils.constants import *
from utils.logger import Logger
from hub.heartbeat import Heartbeat
from motion_sensor.motion_sensor import MotionSensor

def terminate():
    """
        Gracefully shutdown by attempting to gracefully kill all our owned threads, and joining them before killing main
    """
    if hub_heartbeat_thread.is_alive():
        Heartbeat.HUB_HEARTBEAT_THREAD_STATE = KILL
        hub_heartbeat_thread.join()

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

        # Start a thread to ping the Hue hub, if these pings stop working, then perhaps the hub has gone down?
        hub_heartbeat_thread = Thread(target=Heartbeat.hub_heartbeat)
        hub_heartbeat_thread.start()

        # Create a motion sensor object, so we can probe the state etc...
        motion_sensor = MotionSensor()

        while Heartbeat.HUB_HEARTBEAT_THREAD_STATE == RUNNING:
            motion_sensor.get_state()
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
