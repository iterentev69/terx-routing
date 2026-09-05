# TerX Routing

Client-specific routing policies and Remnawave Subscription Response Rules for TerX.

## Upstream geodata

TerX uses `runetfreedom/russia-v2ray-rules-dat` as the source of Russian GeoIP/GeoSite data. The upstream project is rebuilt every 6 hours and provides categories such as `ru-blocked`, `ru-blocked-community`, `ru-whitelist`, `ru-available-only-inside`, `openai`, `youtube`, `telegram`, `discord` and `category-ads-all`.

## Happ

Profile source: `HAPP/DEFAULT.JSON`.

Happ receives the profile through the Remnawave `routing` response header as `happ://routing/onadd/<base64>`. Happ does not use a remote routing-profile URL in this header, so the Happ profile uses stable upstream `release` URLs for GeoIP/GeoSite data.

## INCY

Profile source: `INCY/DEFAULT.JSON`.

INCY receives an auto-updating routing profile through:

`autorouting: incy://autorouting/onadd/https://raw.githubusercontent.com/iterentev69/terx-routing/main/INCY/DEFAULT.JSON`

INCY periodically re-downloads the routing profile. The GitHub Action checks RunetFreedom every 6 hours and updates the versioned GeoIP/GeoSite release URLs in `INCY/DEFAULT.JSON` when a new upstream release appears.

## Remnawave SRR

Ready-to-import response rules are stored in:

`SRR/response-rules.json`

Current client policy:

- Browser → BROWSER
- Happ → XRAY_JSON + TerX routing header
- INCY → XRAY_BASE64 + INCY autorouting header
- Mihomo family → MIHOMO
- Stash → STASH
- Sing-box family → SINGBOX
- legacy Clash → CLASH
- unknown clients → XRAY_BASE64

## TerX policy

The policy is intentionally conservative:

- private/local and services that require Russian access → DIRECT
- Russian blocked resources and selected global services → PROXY
- ads and Windows telemetry categories → BLOCK
- unmatched traffic → PROXY

The routing policy itself is maintained by TerX and is not overwritten by upstream projects.
