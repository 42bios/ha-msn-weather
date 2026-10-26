"""Constants for the MSN Weather integration."""

from __future__ import annotations

DOMAIN = "msn_weather"

CONF_LANGUAGE = "language"
CONF_MSN_URL = "msn_url"
CONF_API_KEY = "api_key"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_MAP_ZOOM = "map_zoom"
CONF_MAP_WIDTH = "map_width"
CONF_MAP_HEIGHT = "map_height"
CONF_MAP_FRAMES = "map_frames"
CONF_MAP_HIRES = "map_hires"
CONF_MAP_LABELS = "map_labels"
CONF_MAP_FRAME_MS = "map_frame_ms"
CONF_IMAGE_SECRET = "image_secret"
CONF_USE_HOME = "use_home_location"
CONF_CYCLONE_RADIUS = "cyclone_radius"
CONF_CYCLONE_FOCUS = "cyclone_focus"
CONF_CYCLONE_DISTURBANCES = "cyclone_disturbances"

DEFAULT_NAME = "MSN Weather"
DEFAULT_LANGUAGE = "en-us"
DEFAULT_SCAN_INTERVAL = 15  # minutes
MIN_SCAN_INTERVAL = 5
DEFAULT_MAP_ZOOM = 8
DEFAULT_MAP_WIDTH = 800
DEFAULT_MAP_HEIGHT = 500
DEFAULT_MAP_FRAMES = 12
DEFAULT_MAP_FRAME_MS = 700  # animation: milliseconds per frame
DEFAULT_CYCLONE_RADIUS = 0  # km, 0 = worldwide
DEFAULT_CYCLONE_FOCUS = "strongest"  # strongest | nearest
CYCLONE_AUTO = "auto"

# Public key used by the msn.com weather web app. MSN may rotate it; it can be
# overridden in the integration options.
DEFAULT_API_KEY = "j5i4gDqHL6nGYwx5wi5kRhXjtf2c5qgFX9fzfk0TOo"
APP_ID = "9e21380c-ff19-4c78-b4ea-19558e93a5d3"
API_URL = "https://assets.msn.com/service/weather/overview"
HURRICANE_LIST_URL = "https://api.msn.com/weather/hurricane/list"
HURRICANE_DETAIL_URL = "https://api.msn.com/weather/hurricane/detail"
WEATHERTRENDS_URL = "https://assets.msn.com/service/weather/weathertrends"

LANGUAGES = [
    "de-de",
    "de-at",
    "de-ch",
    "it-it",
    "en-us",
    "en-gb",
    "fr-fr",
    "es-es",
    "nl-nl",
]

ATTRIBUTION = "Data provided by MSN Weather (Microsoft)"

# Life index sub types as used by the MSN web app (enum "LifeSubType").
LIFE_SUBTYPES: dict[int, str] = {
    1: "dressing",
    2: "uv",
    3: "wind_chill",
    4: "heat_stroke",
    10: "umbrella",
    11: "outdoor",
    12: "driving",
    20: "cycling",
    21: "gardening",
    22: "hiking",
    24: "running",
    25: "stargazing",
    26: "walking",
    27: "picnic",
}
