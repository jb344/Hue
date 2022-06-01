# IP address of Hue hub on the local network
HUE_HUB_IP = "192.168.1.27"
# Username of the privileged user we generated on the hub
HUE_HUB_USERNAME = "mqWIXtAw754p0v7YrkxGcLSwGCtL2dNhFCdBZRTo"
# "Root" of all useful URL. In most of the commands (the exceptions are creating a username and getting basic
# bridge information – Login Required) you’ll also include a username after this
HUE_HUB_LANDING = "http://" + HUE_HUB_IP + "/api"
# The base useful URL, from here is where we can reach light, sensors etc...
HUE_HUB_BASE_URL = HUE_HUB_LANDING + "/" + HUE_HUB_USERNAME

# How often we should ping the hub, in seconds
HUB_HEARTBEAT_INTERVAL_SECONDS = 120

# Time period the lights should stay on for after the motion sensor is triggered
STAY_ON_FOR_X_MINUTES = 5

# All of the light, sensors, routines etc... are all addressable using the URLs listed below
LIGHTS_URL = "/lights"
GROUPS_URL = "/groups"
CONFIG_URL = "/config"
SCHEDULES_URL = "/schedules"
SCENES_URL = "/scenes"
SENSORS_URL = "/sensors"
RULES_URL = "/rules"

# Accessory parameters
STATE_URL = "/state"

# Unique names of all devices on my Hue hub
HALLWAY_MOTION_SENSOR = "Hallway motion sensor"
KITCHEN_MOTION_SENSOR = "Kitchen motion sensor"
LIVING_ROOM_LAMP = "Living room lamp"
HUE_PLAY_TV = "Hue play TV"
HUE_PLAY_BOOKCASE = "Hue play bookcase"
BEDROOM_LAMP = "Bedroom lamp"
HALLWAY_SPOT_ONE = "Hallway spot 1"
HALLWAY_SPOT_TWO = "Hallway spot 2"
KITCHEN_COUNTER_SPOT = "Hue Argenta kitchen worktop"
KITCHEN_SINK_SPOT = "Hue Argenta kitchen sink"
