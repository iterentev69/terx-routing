import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "HAPP" / "DEFAULT.JSON"

UPSTREAMS = {
    "geoip": "hydraponique/roscomvpn-geoip",
    "geosite": "hydraponique/roscomvpn-geosite",
}


def latest_tag(repo: str) -> str:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "terx-routing-updater",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.load(response)
    return data["tag_name"]


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

geoip_tag = latest_tag(UPSTREAMS["geoip"])
geosite_tag = latest_tag(UPSTREAMS["geosite"])

new_geoip = (
    "https://cdn.jsdelivr.net/gh/"
    f"hydraponique/roscomvpn-geoip@{geoip_tag}/release/geoip.dat"
)
new_geosite = (
    "https://cdn.jsdelivr.net/gh/"
    f"hydraponique/roscomvpn-geosite@{geosite_tag}/release/geosite.dat"
)

changed = (
    config.get("Geoipurl") != new_geoip
    or config.get("Geositeurl") != new_geosite
)

if not changed:
    print(f"Already current: GeoIP={geoip_tag}, GeoSite={geosite_tag}")
    raise SystemExit(0)

# Do not publish a profile that points at unavailable CDN assets.
assert_url(new_geoip)
assert_url(new_geosite)

config["Geoipurl"] = new_geoip
config["Geositeurl"] = new_geosite
config["LastUpdated"] = str(int(time.time()))

with CONFIG.open("w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"Updated: GeoIP={geoip_tag}, GeoSite={geosite_tag}")
