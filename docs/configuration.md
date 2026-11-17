# Configuration

## Location and options

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

## Languages and diagnostics

Entity names, setup, options and cards are translated into English, German, Italian, French, Spanish and Dutch.
The MSN texts and map labels use the language chosen in the options, the cards the language of the logged-in user
(other languages show English); every card accepts `language: en | de | it | fr | es | nl` to override it.

*Settings → Devices & services → MSN Weather → ⋮ → Download diagnostics* produces a report without location,
name or keys – attach it to bug reports.

## Data sources

The data comes from the same endpoints the MSN website uses (weather model Foreca, pollen polleninfo.org,
tropical cyclones NHC/JMA/CMA).

## Development

```bash
pip install -r requirements_test.txt
pytest                        # unit tests with recorded MSN responses (tests/fixtures, New York)
python scripts/live_check.py  # checks the real MSN endpoints – also runs weekly in CI
```

[← Back to the README](../README.md)
