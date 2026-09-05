# TerX Routing

Routing policy for Happ clients used by TerX Proxy.

The policy is maintained here, while GeoIP/GeoSite databases are consumed from the upstream `hydraponique/roscomvpn-geoip` and `hydraponique/roscomvpn-geosite` projects.

## Happ profile

`HAPP/DEFAULT.JSON`

Raw URL:

`https://raw.githubusercontent.com/iterentev69/terx-routing/main/HAPP/DEFAULT.JSON`

## Update model

GitHub Actions checks the latest upstream GeoIP and GeoSite releases every 6 hours. If either release changes, the workflow updates the versioned jsDelivr URLs and `LastUpdated` in the Happ profile and commits the change.

The TerX routing policy itself (`DirectSites`, `ProxySites`, `BlockSites`, DNS policy, etc.) is controlled in this repository and is not overwritten by upstream routing-policy changes.
