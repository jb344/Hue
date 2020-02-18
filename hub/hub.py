import subprocess
from time import sleep
import threading

# Defined by me
from utils.constants import *
from hub.config import *


class Hub:
    def __init__(self, logger, found_at_ip: str):
        self.THREAD_STATE = RECOVERABLE                 # State flag of this thread, either RUNNING, RECOVERABLE, or IRRECOVERABLE
        self.THREAD_STATE_MUTEX = threading.Lock()      # Mutex protecting the above flag
        self.HUB_ALIVE = False                          # Is the hub alive?
        self.HUB_ALIVE_MUTEX = threading.Lock()         # Mutex protecting the above flag
        self.LOGGER = logger                            # Logger object
        self.HUE_HUB_IP = found_at_ip                   # IP address of the Hue hub

    def heartbeat(self):
        """
            This is running in its own thread. Ping the Philips Hue hub every 60 seconds. If the hub doesn't reply, we
            set our status to RECOVERABLE in the hopes the main() thread will see it, and attempt to restart us.
        """
        try:
            self.LOGGER.info("Hue hub heartbeat thread started , with interval {}s, IP {}".format(HUB_HEARTBEAT_INTERVAL_SECONDS, self.HUE_HUB_IP))
            self.set_thread_state(RUNNING)

            # The thread state flag can be set to KILL by the main thread, to signify this thread should be terminated
            while self.get_thread_state() != KILL:
                ping_received = False
                # Ping the hub once and return the stdout and stderr of the process to us
                process_result = subprocess.run(args=["ping", self.HUE_HUB_IP, "-c", "1"],
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
                            # Set the hub alive flag to true, then sleep for x seconds before checking again
                            self.set_alive(True)
                            ping_received = True
                            self.LOGGER.debug("Ping received {}".format(ping_result_str))
                            break

                    if not ping_received:
                        # If we hit this line, it's because we didn't receive an ICMP result from the Hub, and thus didn't go
                        # back round the loop
                        self.LOGGER.warning("Ping not received, attempting to continue anyway...")

                sleep(HUB_HEARTBEAT_INTERVAL_SECONDS)

        except Exception as err:
            self.LOGGER.exception(err)
            self.set_alive(False)

    def set_alive(self, value: bool) -> int:
        """
            Set the hub alive flag in a thread-safe manner
                :param value:           Value to set the flag to (either True or False)
                :return:                -1 on failure, 0 on success
        """
        # Acquire the mutex so we can set the hub alive flag
        with self.HUB_ALIVE_MUTEX:
            self.HUB_ALIVE = value

        return SUCCESS

    def get_alive(self) -> bool:
        """
            Get the hub alive flag in a thread-safe manner
                :return:              Value of the flag
        """
        with self.HUB_ALIVE_MUTEX:
            return self.HUB_ALIVE

    def set_thread_state(self, state: int):
        """
            Set the state of this thread in a thread-safe manner
                :param state:           State to set the thread to
                :return:                -1 on FAILURE, 0 on SUCCESS
        """
        with self.THREAD_STATE_MUTEX:
            self.THREAD_STATE = state

        return SUCCESS

    def get_thread_state(self) -> int:
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
        self.THREAD_STATE = KILL
