import base64
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HAPP_JSON = ROOT / "HAPP" / "DEFAULT.JSON"
HAPP_DEEPLINK = ROOT / "HAPP" / "DEFAULT.DEEPLINK"
INCY_JSON = ROOT / "INCY" / "DEFAULT.JSON"

HAPP_UPSTREAM_JSON = "https://raw.githubusercontent.com/hydraponique/roscomvpn-routing/main/HAPP/DEFAULT.JSON"
INCY_UPSTREAM_JSON = "https://raw.githubusercontent.com/hydraponique/roscomvpn-routing/main/INCY/DEFAULT.JSON"
HAPP_NAME = "TerX Smart Routing"
INCY_NAME = "TerXSmartRouting"


def get_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "terx-routing-updater",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def write_pretty_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def build_happ_deeplink(config: dict) -> str:
    compact = json.dumps(config, ensure_ascii=False, separators=(",", ":"))
    payload = base64.b64encode(compact.encode("utf-8")).decode("ascii")
    return f"happ://routing/onadd/{payload}\n"


def sync_happ() -> bool:
    upstream = get_json(HAPP_UPSTREAM_JSON)
    upstream["Name"] = HAPP_NAME

    current_json = None
    if HAPP_JSON.exists():
        with HAPP_JSON.open("r", encoding="utf-8") as f:
            current_json = json.load(f)

    expected_deeplink = build_happ_deeplink(upstream)
    current_deeplink = HAPP_DEEPLINK.read_text(encoding="utf-8") if HAPP_DEEPLINK.exists() else None

    changed = current_json != upstream or current_deeplink != expected_deeplink
    if not changed:
        print("HAPP already current with RoscomVPN upstream")
        return False

    write_pretty_json(HAPP_JSON, upstream)
    HAPP_DEEPLINK.write_text(expected_deeplink, encoding="utf-8")
    print("Updated HAPP profile from RoscomVPN and regenerated compact deeplink")
    return True


def sync_incy() -> bool:
    upstream = get_json(INCY_UPSTREAM_JSON)
    upstream["Name"] = INCY_NAME

    current_json = None
    if INCY_JSON.exists():
        with INCY_JSON.open("r", encoding="utf-8") as f:
            current_json = json.load(f)

    if current_json == upstream:
        print("INCY already current with RoscomVPN upstream")
        return False

    write_pretty_json(INCY_JSON, upstream)
    print("Updated INCY profile from RoscomVPN with no-space TerX branding")
    return True


if __name__ == "__main__":
    happ_changed = sync_happ()
    incy_changed = sync_incy()
    if not happ_changed and not incy_changed:
        print("No routing updates required")
