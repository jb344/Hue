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

    if motion_detected_thread.is_alive():
        motion_sensor.kill_thread()
        motion_detected_thread.join()

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

        # Create the Hub and Motion Sensor objects we need, from the config file values
        hub = Hub(logger=log, found_at_ip=HUE_HUB_IP)
        motion_sensor = MotionSensor(logger=log, motion_sensor_name=MOTION_SENSOR_NAME, connected_to_hub=hub)

        # Start a thread to ping the Hue hub, if these pings stop working, then perhaps the hub has gone down?
        hub_heartbeat_thread = Thread(name="hub_heartbeat_thread", target=hub.heartbeat)
        hub_heartbeat_thread.start()

        # Start a thread to constantly probe the motion sensor for activity
        motion_detected_thread = Thread(name="motion_detected_thread", target=motion_sensor.interrogate)
        motion_detected_thread.start()

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
            if motion_sensor.get_thread_state() == RECOVERABLE:
                # If its still alive then kill it
                if motion_detected_thread.is_alive():
                    motion_sensor.kill_thread()
                    motion_detected_thread.join()

                # Restart it
                motion_detected_thread = Thread(name="motion_detected_thread", target=motion_sensor.interrogate)
                motion_detected_thread.start()

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
