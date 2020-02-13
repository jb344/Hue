import subprocess
from time import sleep

# Defined by me
from utils.constants import *
from config import *
from utils.logger import Logger


class Heartbeat:
    HUB_HEARTBEAT_THREAD_STATE = None

    @staticmethod
    def hub_heartbeat():
        """
            This is running in its own thread. Ping the Philips Hue heartbeat every 60 seconds. If the heartbeat doesn't reply, we
            set our status to RECOVERABLE in the hopes the main() thread will see it, and attempt to restart us.
                :return:        RECOVERABLE if the thread for some reason receives no ping reply
        """
        log = None

        try:
            log = Logger.get_logger()
            Heartbeat.HUB_HEARTBEAT_THREAD_STATE = RUNNING

            while Heartbeat.HUB_HEARTBEAT_THREAD_STATE != KILL:
                process_result = subprocess.run(args=["ping", HUE_HUB_IP, "-c", "1"],
                                                stderr=subprocess.PIPE,
                                                stdout=subprocess.PIPE)

                if process_result.check_returncode() == ERROR:
                    raise RuntimeError(process_result.stderr)
                else:
                    ping_result_str = process_result.stdout.decode()
                    for lines in ping_result_str.splitlines():
                        if "1 received" in lines:
                            sleep(60)
                            break

                # If we hit this line, it's because we didn't receive an ICMP result from the Hub, and thus didn't go
                # back round the loop
                raise RuntimeError("Ping not received from the Hue Hub at {}".format(HUE_HUB_IP))
        except Exception as err:
            log.exception(err)
            Heartbeat.HUB_HEARTBEAT_THREAD_STATE = RECOVERABLE
            return RECOVERABLE
