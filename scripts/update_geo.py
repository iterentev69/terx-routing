import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "INCY" / "DEFAULT.JSON"
UPSTREAM = "runetfreedom/russia-v2ray-rules-dat"


def latest_release(repo: str) -> dict:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "terx-routing-updater",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def assert_url(url: str) -> None:
    req = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "terx-routing-updater"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"URL validation failed ({response.status}): {url}")


with CONFIG.open("r", encoding="utf-8") as f:
    config = json.load(f)

release = latest_release(UPSTREAM)
tag = release["tag_name"]
assets = {asset["name"]: asset["browser_download_url"] for asset in release.get("assets", [])}

try:
    new_geoip = assets["geoip.dat"]
    new_geosite = assets["geosite.dat"]
except KeyError as exc:
    raise RuntimeError(f"Required release asset is missing: {exc.args[0]}") from exc

changed = (
    config.get("Geoipurl") != new_geoip
    or config.get("Geositeurl") != new_geosite
)

if not changed:
    print(f"Already current: RunetFreedom={tag}")
    raise SystemExit(0)

assert_url(new_geoip)
assert_url(new_geosite)

config["Geoipurl"] = new_geoip
config["Geositeurl"] = new_geosite
config["LastUpdated"] = str(int(time.time()))

with CONFIG.open("w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"Updated INCY profile: RunetFreedom={tag}")
