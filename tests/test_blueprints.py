"""The shipped automation blueprints are valid and fill in their inputs."""

from __future__ import annotations

from pathlib import Path

import pytest
from homeassistant.components.automation.config import async_validate_config_item
from homeassistant.components.blueprint import models
from homeassistant.components.blueprint.schemas import BLUEPRINT_SCHEMA
from homeassistant.core import HomeAssistant
from homeassistant.util.yaml import load_yaml

BLUEPRINTS = sorted((Path(__file__).parent.parent / "blueprints" / "automation" / "msn_weather").glob("*.yaml"))
INPUTS = {
    "alert_sensor": "binary_sensor.upper_east_side_alert_active",
    "umbrella_sensor": "sensor.upper_east_side_umbrella",
    "cyclone_sensor": "binary_sensor.upper_east_side_cyclone_nearby",
    "actions": [{"action": "persistent_notification.create", "data": {"message": "test"}}],
}


@pytest.mark.parametrize("path", BLUEPRINTS, ids=lambda p: p.stem)
async def test_blueprint(hass: HomeAssistant, path: Path) -> None:
    data = load_yaml(path)
    blueprint = models.Blueprint(data, expected_domain="automation", schema=BLUEPRINT_SCHEMA)
    used = {k: v for k, v in INPUTS.items() if k in blueprint.inputs}
    inputs = models.BlueprintInputs(blueprint, {"use_blueprint": {"path": path.name, "input": used}})
    inputs.validate()
    config = inputs.async_substitute()
    config["id"] = path.stem
    assert config["triggers"]
    # the filled-in automation passes Home Assistant's automation validation
    result = await async_validate_config_item(hass, path.stem, config)
    assert result is not None
    assert result.validation_error is None, result.validation_error
