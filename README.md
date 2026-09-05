# TerX Routing

Client-specific routing policies and Remnawave Subscription Response Rules for TerX.

## Happ

Source of truth: `HAPP/DEFAULT.JSON`.

Every 6 hours GitHub Actions fetches the current RoscomVPN `HAPP/DEFAULT.JSON`, changes only `Name` to `TerX Smart Routing`, writes the TerX JSON and regenerates `HAPP/DEFAULT.DEEPLINK` from compact/minified JSON.

The compact serialization is intentional: Happ was observed to parse the pretty-printed deeplink differently and fall back to `1.1.1.1` for `RemoteDNSIP`. The workflow validates that the deeplink decodes exactly to `HAPP/DEFAULT.JSON` and that `RemoteDNSIP` remains `8.8.8.8`.

`remna-routing-updater` does not generate the deeplink. It reads the ready `HAPP/DEFAULT.DEEPLINK` from GitHub and writes it into the Remnawave `routing` response header when it changes.

Happ must receive `XRAY_BASE64`; client-side routing profiles are not applied as expected to `XRAY_JSON` subscriptions.

## INCY

Source of truth: `INCY/DEFAULT.JSON`.

INCY keeps the current TerX policy while its RunetFreedom GeoIP/GeoSite release URLs are automatically refreshed every 6 hours.

Current INCY policy:

- DIRECT domains: `private`, `category-ru`, `ru-available-only-inside`, `microsoft`, `apple`
- DIRECT IP: `private`, `ru-whitelist`
- PROXY domains: `ru-blocked`, `openai`, `google`, `google-play`, `youtube`, `telegram`, `discord`, `github`
- PROXY IP: `ru-blocked`, `ru-blocked-community`, `re-filter`, `google`, `telegram`
- BLOCK domains: `category-ads-all`, `win-spy`
- unmatched traffic: PROXY (`GlobalProxy=true`)

INCY receives the profile through:

`autorouting: incy://autorouting/onadd/https://raw.githubusercontent.com/iterentev69/terx-routing/main/INCY/DEFAULT.JSON`

## Remnawave SRR

Ready-to-import response rules are stored in:

`SRR/response-rules.json`

Current client policy:

- Browser → BROWSER
- Happ → XRAY_BASE64 + `routing` header maintained by `remna-routing-updater`
- INCY → XRAY_BASE64 + INCY `autorouting` header
- Mihomo family → MIHOMO
- Stash → STASH
- Sing-box family → SINGBOX
- legacy Clash → CLASH
- unknown clients → XRAY_BASE64

## Automation flow

```text
RoscomVPN HAPP/DEFAULT.JSON
          |
          v
GitHub Action every 6h
          |
          +--> HAPP/DEFAULT.JSON (Name = TerX Smart Routing)
          |
          +--> compact JSON -> base64 -> HAPP/DEFAULT.DEEPLINK
                                      |
                                      v
                           remna-routing-updater
                                      |
                                      v
                              Remnawave routing header
                                      |
                                      v
                                    Happ

RunetFreedom latest release
          |
          v
GitHub Action every 6h
          |
          v
INCY/DEFAULT.JSON GeoIP/GeoSite URLs
          |
          v
INCY autorouting remote profile
```
