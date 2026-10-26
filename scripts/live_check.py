"""Check the real MSN endpoints (weekly CI run).

Catches changes on Microsoft's side – a rotated key, renamed fields, moved endpoints.
Run from the repository root:  python scripts/live_check.py
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys

import aiohttp

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from custom_components.msn_weather.api import (  # noqa: E402
    MsnWeatherClient,
    async_discover_api_key,
)
from custom_components.msn_weather.const import DEFAULT_API_KEY  # noqa: E402
from custom_components.msn_weather.maps import MsnMapRenderer  # noqa: E402

LAT, LON = 40.7736, -73.9566  # New York, Upper East Side
problems: list[str] = []


def check(ok: bool, message: str) -> None:
    print(("ok    " if ok else "FAIL  ") + message)
    if not ok:
        problems.append(message)


async def main() -> int:
    async with aiohttp.ClientSession() as session:
        key = await async_discover_api_key(session)
        check(bool(key), "apiKey found on msn.com")
        check(key in (None, DEFAULT_API_KEY), f"public key unchanged (msn.com uses {key})")
        key = key or DEFAULT_API_KEY

        for imperial in (False, True):
            data = await MsnWeatherClient(session, LAT, LON, "en-us", key, imperial=imperial).async_get()
            label = "imperial" if imperial else "metric"
            check(data.current.get("temp") is not None, f"overview ({label}): current temperature")
            check(len(data.days) >= 10 and len(data.hourly) > 100, f"overview ({label}): 10 days, hourly")
            check(bool(data.life_today), f"overview ({label}): life indices")
            check(bool(data.insights), f"overview ({label}): weather detail texts")

        client = MsnWeatherClient(session, LAT, LON, "en-us", key)
        climate, monthly = await client.async_get_climate()
        check(bool(climate.get("days")), "weathertrends: climate normals")
        check(len(monthly) >= 28, "weathertrends: monthly calendar")
        storms = await client.async_get_storms()  # may be empty out of season
        check(all(s["name"] and s["latitude"] is not None for s in storms), f"hurricanes: {len(storms)} parsed")
        meta = await MsnMapRenderer(session, key, "en-us").metadata()
        check(bool(meta), "maps: metadata")
        for name in ("NowcastVectorMap", "NowcastVectorMapHistory"):
            uris = (meta or {}).get(name, {}).get("uris") or {}
            check(bool(uris), f"radar: {name} in metadata")
            for version, url in uris.items():
                tile = url.format(x=0, y=0, z=0, time=version).replace(".blc", ".json")
                async with session.get(tile) as resp:
                    check(resp.status == 200, f"radar: {name} tile reachable")

    print(f"\n{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
