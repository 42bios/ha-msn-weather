# Entities

Entity IDs are language independent: `<domain>.<entry name>_<key>`, e.g. `sensor.upper_east_side_umbrella`,
`image.upper_east_side_map_precipitation` or `number.upper_east_side_map_forecast_hours` – only the displayed names are
translated. The examples use an entry named "Upper East Side".

## Weather entity `weather.<name>`
Forecasts via `weather.get_forecasts`:

| Type | Range | Fields |
|---|---|---|
| `hourly` | ~220 hours | condition, temperature, feels like, dew point, humidity, pressure, precipitation, probability, wind, gusts, bearing, cloud cover, UV, `visibility`, `aqi` |
| `daily` | 10 days | high/low, feels like, precipitation, probability, wind and gusts, UV, humidity, cloud cover, pressure/visibility ranges, rain day/night, pollen, sunrise/sunset, moonrise/moonset, `summary` |
| `twice_daily` | 10 days, day and night | condition, temperature, probability, wind, `summary` |

## Sensors (weather details)
Every sensor carries the texts of the MSN tile as attributes: `headline`, `summary`, `details`, `trend`; tile
sensors additionally carry `today_series` (the hourly curve of today).

| Tile | Sensors |
|---|---|
| Temperature / feels like | temperature, today's high/low, feels like, dew point |
| Cloud cover | condition (text), cloud cover % |
| Precipitation | precipitation today, probability, precipitation next 2 h (nowcast: MSN text, 4 minute values, `template_type`, `minutes_to_change`), "precipitation change in" (minutes until rain starts/stops) |
| Wind | speed, gusts, bearing (degrees and text) |
| Humidity, UV, visibility, pressure | one sensor each |
| AQI | index, O₃, PM2.5, PM10, NO₂, CO, SO₂; attribute `forecast` with hourly pollutant values |
| Pollen | index with level, main allergen, per pollen type, forecast |
| Sun / moon | rise/set, day length, moon visible, moon phase, illumination, next full moon |
| Alerts | number of weather alerts (list as attribute, with `source` = the national weather service, e.g. NWS, Météo-France, MeteoSwiss, JMA) and binary sensor "alert active"; `significance` is R / O / Y / B (red / orange / yellow / blue) for every country |
| Tropical cyclones | number of active storms within the configured radius (worldwide when 0); attributes `nearest`, `strongest`, `storms` (name, category, wind, position, distance, closest forecast approach), `worldwide`; binary sensor "tropical cyclone nearby" |
| Yesterday | high/low, precipitation; optional feels like, wind/gusts, humidity, pressure, UV, visibility, cloud cover |
| Daily details | attribute `days`: per day (yesterday … +9) highs/lows of all values, rain day/night, pollen, sun/moon, MSN texts |
| Climate | normal high/low for today, record high/low (with year), normal precipitation (with records, snow, wind) – data since 1951 |
| Monthly forecast | attribute `days`: ~40 days with condition, high/low, rain probability, wind |

## Sensors (life indices)
State = MSN short text ("Light jacket", "Not needed", "Great"). Attributes: `summary`, `category` (1 = good …
5 = poor), `value`, the values for tomorrow and `hourly` (hourly outlook for today and tomorrow).

- **Health and safety:** umbrella, outdoors/walking, UV exposure, driving, clothing, heat stroke, wind chill
- **Activities** (disabled by default): cycling, gardening, hiking, running, stargazing, picnic

The weather maps (image entities) are described in [maps.md](maps.md).

[← Back to the README](../README.md)
