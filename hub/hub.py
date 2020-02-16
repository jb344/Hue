import subprocess
from time import sleep
import threading

# Defined by me
from utils.constants import *
from hub.config import *
from utils.logger import Logger


class Heartbeat:
    HUB_HEARTBEAT_THREAD_STATE = None
    HUB_ALIVE = False
    HUB_ALIVE_MUTEX = threading.Lock()

    @staticmethod
    def hub_heartbeat():
        """
            This is running in its own thread. Ping the Philips Hue hub every 60 seconds. If the hub doesn't reply, we
            set our status to RECOVERABLE in the hopes the main() thread will see it, and attempt to restart us.
        """
        log = None

        try:
            log = Logger.get_logger()
            Heartbeat.HUB_HEARTBEAT_THREAD_STATE = RUNNING

            # The thread state flag can be set to KILL by the main thread, to signify this thread should be terminated
            while Heartbeat.HUB_HEARTBEAT_THREAD_STATE != KILL:
                # Ping the hub once and return the stdout and stderr of the process to us
                process_result = subprocess.run(args=["ping", HUE_HUB_IP, "-c", "1"],
                                                stderr=subprocess.PIPE,
                                                stdout=subprocess.PIPE)

                # If the return code is -1 then raise an error
                if process_result.check_returncode() == ERROR:
                    raise ValueError(process_result.stderr)
                else:
                    # stdout is returned as raw bytes, so decode it into a string object
                    ping_result_str = process_result.stdout.decode()
                    for lines in ping_result_str.splitlines():
                        # Check the ping statistics and if it contains the text "1 received" it means a reply was found
                        if "1 received" in lines:
                            # Set the hub alive flag to true, then sleep for 60 seconds before checking again
                            Heartbeat.set_alive_flag(True)
                            sleep(60)
                            break

                # If we hit this line, it's because we didn't receive an ICMP result from the Hub, and thus didn't go
                # back round the loop
                raise RuntimeError("Ping not received from the Hue Hub at {}".format(HUE_HUB_IP))

        except Exception as err:
            log.exception(err)
            Heartbeat.set_alive_flag(False)

    @staticmethod
    def set_alive_flag(value: bool):
        """
            Set the hub alive flag in a thread-safe manner
                :param value:           Value to set the flag to (either True or False)
                :return:
        """
        # Acquire the mutex so we can set the hub alive flag
        with Heartbeat.HUB_ALIVE_MUTEX:
            Heartbeat.HUB_ALIVE = value

        return SUCCESS

    @staticmethod
    def get_alive_flag():
        with Heartbeat.HUB_ALIVE_MUTEX:
            return Heartbeat.HUB_ALIVE
