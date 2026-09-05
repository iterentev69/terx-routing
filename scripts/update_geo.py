import base64
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HAPP_JSON = ROOT / "HAPP" / "DEFAULT.JSON"
HAPP_DEEPLINK = ROOT / "HAPP" / "DEFAULT.DEEPLINK"
INCY_JSON = ROOT / "INCY" / "DEFAULT.JSON"

HAPP_UPSTREAM_JSON = "https://raw.githubusercontent.com/hydraponique/roscomvpn-routing/main/HAPP/DEFAULT.JSON"
RUNETFREEDOM_UPSTREAM = "runetfreedom/russia-v2ray-rules-dat"
TERX_NAME = "TerX Smart Routing"


def get_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "terx-routing-updater",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def latest_release(repo: str) -> dict:
    return get_json(f"https://api.github.com/repos/{repo}/releases/latest")


def assert_url(url: str) -> None:
    req = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "terx-routing-updater"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"URL validation failed ({response.status}): {url}")


def write_pretty_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def build_happ_deeplink(config: dict) -> str:
    # Happ is sensitive to the serialized payload. Keep this identical to
    # RoscomVPN's compact JSON form before base64 encoding.
    compact = json.dumps(config, ensure_ascii=False, separators=(",", ":"))
    payload = base64.b64encode(compact.encode("utf-8")).decode("ascii")
    return f"happ://routing/onadd/{payload}\n"


def sync_happ() -> bool:
    upstream = get_json(HAPP_UPSTREAM_JSON)
    upstream["Name"] = TERX_NAME

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
    with INCY_JSON.open("r", encoding="utf-8") as f:
        config = json.load(f)

    release = latest_release(RUNETFREEDOM_UPSTREAM)
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
        print(f"INCY already current: RunetFreedom={tag}")
        return False

    assert_url(new_geoip)
    assert_url(new_geosite)

    config["Geoipurl"] = new_geoip
    config["Geositeurl"] = new_geosite
    config["LastUpdated"] = str(int(time.time()))
    write_pretty_json(INCY_JSON, config)

    print(f"Updated INCY profile: RunetFreedom={tag}")
    return True


if __name__ == "__main__":
    happ_changed = sync_happ()
    incy_changed = sync_incy()
    if not happ_changed and not incy_changed:
        print("No routing updates required")
