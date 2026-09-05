import base64
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "HAPP" / "DEFAULT.JSON"
DEEPLINK_PATH = ROOT / "HAPP" / "DEFAULT.DEEPLINK"
UPSTREAM_URL = "https://raw.githubusercontent.com/hydraponique/roscomvpn-routing/main/HAPP/DEFAULT.JSON"
BRANDED_NAME = "TerX Smart Routing"


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "terx-routing-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


profile = fetch_json(UPSTREAM_URL)
profile["Name"] = BRANDED_NAME

content = json.dumps(profile, ensure_ascii=False, indent=2) + "\n"
deeplink = "happ://routing/onadd/" + base64.b64encode(content.encode("utf-8")).decode("ascii")

PROFILE_PATH.write_text(content, encoding="utf-8")
DEEPLINK_PATH.write_text(deeplink + "\n", encoding="utf-8")

print("Synced Happ routing from RoscomVPN and preserved branded profile name")
