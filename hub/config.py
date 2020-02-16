# IP address of my Hue hub on the local network
HUE_HUB_IP = "192.168.1.27"
# Username of the privileged user we generated on the hub
HUE_HUB_USERNAME = "mqWIXtAw754p0v7YrkxGcLSwGCtL2dNhFCdBZRTo"
# "Root" of all useful URL. In most of the commands (the exceptions are creating a username and getting basic
# bridge information – Login Required) you’ll also include a username after this
HUE_HUB_LANDING = "http://" + HUE_HUB_IP + "/api"
# The base useful URL, from here is where we can reach lights, sensors etc...
HUE_HUB_BASE_URL = HUE_HUB_LANDING + "/" + HUE_HUB_USERNAME

# All of the lights, sensors, routines etc... are all addressable using the URLs listed below
LIGHTS_URL = "/lights"
GROUPS_URL = "/groups"
CONFIG_URL = "/config"
SCHEDULES_URL = "/schedules"
SCENES_URL = "/scenes"
SENSORS_URL = "/sensors"
RULES_URL = "/rules"

# Unique names of all devices on my Hue hub
MOTION_SENSOR_NAME = "Hallway motion sensor"
LIVING_ROOM_LAMP = "Living room lamp"
HUE_PLAY = "Hue play"
BEDROOM_LAMP = "Bedroom lamp"
HALLWAY_SPOT_ONE = "Hallway spot 1"
HALLWAY_SPOT_TWO = "Hallway spot 2"
