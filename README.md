# MSN Weather for Home Assistant

<!-- ha-marketplace:exclude-start -->
[![CI](https://github.com/42bios/ha-msn-weather/actions/workflows/validate.yml/badge.svg)](https://github.com/42bios/ha-msn-weather/actions/workflows/validate.yml)
[![Marketplace](https://img.shields.io/badge/Home%20Assistant-Marketplace-41BDF5)](https://my.home-assistant.io/redirect/hacs_repository/?owner=42bios&repository=ha-msn-weather&category=integration)
[![Release](https://img.shields.io/github/v/release/42bios/ha-msn-weather?color=blue)](https://github.com/42bios/ha-msn-weather/releases)
<!-- ha-marketplace:exclude-end -->

Home Assistant custom integration that brings **MSN Weather** (msn.com/weather) to Home Assistant – everything the
website shows, as entities, maps and dashboard cards.

<img src="https://raw.githubusercontent.com/42bios/ha-msn-weather/main/custom_components/msn_weather/brand/icon@2x.png" alt="MSN Weather" width="128">

> **Disclaimer:** This is an unofficial, community-maintained integration and is not affiliated with, endorsed by, or
> supported by Microsoft or MSN. All product names, logos and brands are property of their respective owners and are
> used for identification purposes only.

## Highlights

- **Weather entity** with hourly, daily and day/night forecasts (10 days)
- **Sensors** for all "weather details" tiles, including MSN's texts ("Falling", "Pleasant", …)
- **Life indices**: health and safety (umbrella, driving, clothing, …) and activities, each with an hourly outlook
- **Daily values from yesterday to +9 days**, climate normals and records since 1951 and a ~30 day monthly forecast
- **Minute-by-minute precipitation**: when rain starts and stops in the next 2 hours, and the precipitation radar
- **Weather alerts** with period and safety advice, **tropical cyclones** with a configurable radius
- **Animated weather maps** as image entities (radar, temperature, precipitation, wind, clouds, satellite, severe
  weather, lightning, tropical cyclones, …)
- **Lovelace cards** in MSN style or classic Home Assistant style, shipped with the integration – or a complete
  weather view in one step
- **Blueprints** for alert, umbrella and cyclone notifications

![Weather maps](https://raw.githubusercontent.com/42bios/ha-msn-weather/main/docs/maps.jpg)

## Installation

Requires Home Assistant 2025.1 or newer.

[![Open your Home Assistant instance and open this repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=42bios&repository=ha-msn-weather&category=integration)

The button opens the Marketplace on Home Assistant 2026.11 or newer, and HACS on older versions.

### Marketplace (Home Assistant 2026.11 or newer)
1. Open `Settings -> Marketplace` and search for `MSN Weather`.
2. Install it.

### HACS (older Home Assistant versions)
1. Open HACS and search for `MSN Weather`.
2. Download it and restart Home Assistant.

### Manual
1. Copy `custom_components/msn_weather` into the `custom_components` folder of your Home Assistant configuration.
2. Restart Home Assistant.

## Setup

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=msn_weather)

Add the integration under `Settings -> Devices & services -> Add integration -> MSN Weather`.

- By default the **location of your Home Assistant installation** is used – and followed if you change it later.
- Optionally switch that off and pick another place on the map, or paste an MSN weather URL (it takes precedence),
  e.g. `https://www.msn.com/en-us/weather/forecast/in-New-York,NY?loc=eyJsIjoi...`

The options of the integration offer:

- language of the MSN texts (defaults to your Home Assistant language)
- update interval (default 15 min)
- maps: zoom, image size, animation frames and speed, high resolution, title and legend in the images
  (off = the map card shows them as overlays)
- tropical cyclones: radius, focus, disturbances
- API key (see below)

**Units follow your Home Assistant unit system:** with *US customary* everything is °F, mph, inHg, miles and inches,
with *metric* °C, km/h, hPa, km and mm – values, MSN texts, map legends and cards alike.

> ⚠️ This is an unofficial API and Microsoft may change it at any time. When MSN rotates its public web API key,
> the integration reads the current key from msn.com automatically. If that fails, a repair issue appears
> (*Settings → Repairs*) and you can enter a key in the integration options – you find it in your browser's
> developer tools on msn.com/weather (network tab → request `weather/overview` → parameter `apikey`).

## Weather view in one step

The integration ships a dashboard strategy that builds a complete weather view from all cards (hourly, weather
details, health and safety, activities, monthly forecast and all enabled maps):

```yaml
# a whole dashboard (one view per MSN Weather entry): Settings → Dashboards → Add dashboard →
# "New dashboard from scratch" → ⋮ → Raw configuration editor
strategy:
  type: custom:msn-weather
  appearance: ha          # optional: ha (default) | msn
  maps: true              # optional
  life: tiles             # optional: tiles (default, one tile per index) | cards

# or a single view inside an existing dashboard
views:
  - strategy:
      type: custom:msn-weather
      entity: weather.upper_east_side   # optional, default: first MSN Weather entry
```

Take control (⋮ → *Take control*) to turn the generated view into normal cards you can edit.

## Lovelace cards

<p align="center"><img src="https://raw.githubusercontent.com/42bios/ha-msn-weather/main/docs/cards-hourly.jpg" alt="Hourly and minute-by-minute precipitation" width="49%"> <img src="https://raw.githubusercontent.com/42bios/ha-msn-weather/main/docs/cards-details.jpg" alt="Weather detail tiles and health and safety" width="49%"></p>

The integration ships eleven cards and loads them automatically – no resource needs to be added. All cards have a
visual editor, appear in the card picker as "MSN Weather – …" and come in two appearances: `msn` (looks like
msn.com) and `ha` (classic Home Assistant look).

| Card | Content |
|---|---|
| `custom:msn-weather-tile-card` | one weather detail tile |
| `custom:msn-weather-details-card` | all weather detail tiles in one card |
| `custom:msn-weather-hourly-card` | day cards (yesterday … +9) and an hourly chart with tabs |
| `custom:msn-weather-rain-card` | when rain or snow starts, how long it lasts and how much falls |
| `custom:msn-weather-rain-chart-card` | precipitation per hour as bars |
| `custom:msn-weather-nowcast-card` | precipitation of the next 2 hours in 4 minute steps |
| `custom:msn-weather-alerts-card` | active and upcoming weather warnings with safety advice |
| `custom:msn-weather-life-tile-card` | one life index (umbrella, cycling, driving, …) as a tile |
| `custom:msn-weather-life-card` | health and safety / activities with an hourly bar chart |
| `custom:msn-weather-monthly-card` | calendar with the monthly forecast, climate normals and records |
| `custom:msn-weather-map-card` | animated weather map |

All options and YAML examples: [docs/cards.md](https://github.com/42bios/ha-msn-weather/blob/main/docs/cards.md).

## Entities and maps

- [docs/entities.md](https://github.com/42bios/ha-msn-weather/blob/main/docs/entities.md) – weather entity,
  sensors and their attributes, life indices
- [docs/maps.md](https://github.com/42bios/ha-msn-weather/blob/main/docs/maps.md) – the animated weather maps,
  map forecast and zoom, tropical cyclone options and how the maps are built

The data comes from the same endpoints the MSN website uses (weather model Foreca, pollen polleninfo.org,
tropical cyclones NHC/JMA/CMA).

## Blueprints

Ready-made automations in [`blueprints/automation/msn_weather`](https://github.com/42bios/ha-msn-weather/tree/main/blueprints/automation/msn_weather) –
import them via *Settings → Automations & scenes → Blueprints → Import blueprint* with the file's GitHub URL, or
copy them to `<config>/blueprints/automation/msn_weather/`:

| Blueprint | Triggers | Variables for the message |
|---|---|---|
| Severe weather alert | a weather warning becomes active | `title`, `level`, `description` |
| Umbrella reminder | at a set time, if the umbrella index reaches a category (language independent) | `state`, `summary` |
| Tropical cyclone nearby | a storm enters (or is forecast to enter) the configured radius | `storms`, `closest_km` |

The actions are up to you, e.g. a notification to the companion app.

## Languages and diagnostics

Entity names, setup, options and cards are translated into English, German, Italian, French, Spanish and Dutch.
The MSN texts and map labels use the language chosen in the options, the cards the language of the logged-in user
(other languages show English); every card accepts `language: en | de | it | fr | es | nl` to override it.

*Settings → Devices & services → MSN Weather → ⋮ → Download diagnostics* produces a report without location,
name or keys – attach it to bug reports.

<!-- ha-marketplace:exclude-start -->
## Development

```bash
pip install -r requirements_test.txt
pytest                        # unit tests with recorded MSN responses (tests/fixtures, New York)
python scripts/live_check.py  # checks the real MSN endpoints – also runs weekly in CI
```
<!-- ha-marketplace:exclude-end -->

## Support

- Issues: https://github.com/42bios/ha-msn-weather/issues

<a href="https://www.buymeacoffee.com/42bios">
  <img
    src="https://cdn.buymeacoffee.com/buttons/v2/arial-yellow.png"
    alt="Buy Me a Coffee"
    width="140"
  />
</a>

## License

MIT – see [LICENSE](LICENSE).
