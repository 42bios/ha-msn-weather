# Blueprints

Ready-made automations in [`blueprints/automation/msn_weather`](../blueprints/automation/msn_weather) –
import them via *Settings → Automations & scenes → Blueprints → Import blueprint* with the file's GitHub URL, or
copy them to `<config>/blueprints/automation/msn_weather/`:

| Blueprint | Triggers | Variables for the message |
|---|---|---|
| Severe weather alert | a weather warning becomes active | `title`, `level`, `description` |
| Umbrella reminder | at a set time, if the umbrella index reaches a category (language independent) | `state`, `summary` |
| Tropical cyclone nearby | a storm enters (or is forecast to enter) the configured radius | `storms`, `closest_km` |

The actions are up to you, e.g. a notification to the companion app.

[← Back to the README](../README.md)
