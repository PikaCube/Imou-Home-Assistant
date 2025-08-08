"""Constants."""

# Internal constants
DOMAIN = "imou_life"

# Configuration definitions
CONF_API_URL_SG = "openapi-sg.easy4ip.com"
CONF_API_URL_OR = "openapi-or.easy4ip.com"
CONF_API_URL_FK = "openapi-fk.easy4ip.com"
CONF_API_URL_HZ = "openapi.lechange.cn"

CONF_HD = "HD"
CONF_SD = "SD"

CONF_HTTP = "http"
CONF_HTTPS = "https"


# parameters:
PARAM_API_URL = "api_url"
PARAM_APP_ID = "app_id"
PARAM_APP_SECRET = "app_secret"
PARAM_MOTION_DETECT = "motion_detect"
PARAM_STATUS = "status"
PARAM_STORAGE_USED = "storage_used"
PARAM_HEADER_DETECT = "header_detect"
PARAM_CURRENT_OPTION = "current_option"
PARAM_OPTIONS = "options"
PARAM_RESTART_DEVICE = "restart_device"
PARAM_UPDATE_INTERVAL = "update_interval"
PARAM_DOWNLOAD_SNAP_WAIT_TIME = "download_snap_wait_time"
PARAM_LIVE_RESOLUTION = "live_resolution"
PARAM_LIVE_PROTOCOL = "live_protocol"
PARAM_ROTATION_DURATION = "rotation_duration"
PARAM_ENTITY_ID = "entity_id"
PARAM_PTZ = "ptz"
PARAM_OPTION = "option"
PARAM_COUNT_DOWN_SWITCH = "count_down_switch"
PARAM_OVERCHARGE_SWITCH = "overcharge_switch"
PARAM_USE_LOCAL_STREAM = "use_local_stream"
PARAM_RTSP_URL = "rtsp_url"
PARAM_USERNAME = "username"
PARAM_PASSWORD = "password"

# service
SERVICE_RESTART_DEVICE = "restart_device"
SERVICE_CONTROL_MOVE_PTZ = "control_move_ptz"
SERVICE_TURN_ON = "turn_on"
SERVICE_TURN_OFF = "turn_off"
SERVICE_SELECT = "select"


PLATFORMS = ["select", "sensor", "switch", "camera", "button", "binary_sensor", "text"]
