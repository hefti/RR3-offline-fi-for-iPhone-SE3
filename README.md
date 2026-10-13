# RR3 offline fix for iPhone SE 3

**RR3 offline - fix for iPhone SE3** fixes the **33 MB additional-data download stall** in the preserved Real Racing 3 14.0.1 iOS package.

## Current working baseline — 13 October 2026

**The owner reports that the current installation works**, with perhaps 1–2 black backgrounds that they consider acceptable. Preserve this working setup; resolving those cosmetic gaps or completing the asset inventory is optional and does not require reinstalling or replacing the current cache.

The earlier inventory reported **24,791 of 24,792 resources present**. The one missing file is `SpeedRush_TV_commercial.mp4`, referenced by `asset_list_quest_speedrush_assets.txt`. Its relationship to the black backgrounds is unknown. These are prior findings and owner feedback, not a new device test or resource scan.

See [current status and preservation](STATUS.md), the [optional roadmap](ROADMAP.md), and [tracked tasks](https://github.com/hefti/RR3-offline-fix-for-iPhone-SE3/issues). The existing `v1.0-se3` release remains the reference IPA; this documentation update changes no game files or release assets.

## Download and install — no Python needed

**[Download the ready-made fixed IPA](https://github.com/hefti/RR3-offline-fix-for-iPhone-SE3/releases/download/v1.0-se3/RR3-SE3-HD-Test-v1.ipa)** · about 1.37 GB · [Release notes and checksum](https://github.com/hefti/RR3-offline-fix-for-iPhone-SE3/releases/tag/v1.0-se3)

> **Installation base:** [Indegosblade/RR3-DevOps v1.0 Production Quality](https://github.com/Indegosblade/RR3-DevOps/releases/tag/v1.0-4k), with the matching [v1.0 asset cache](https://github.com/Indegosblade/RR3-DevOps/releases/tag/v1.0-cache). The fixed IPA already includes that base and the SE 3 fix. Install the fixed IPA directly; no separate installation of the original IPA is needed.

1. Download the fixed IPA above and load it into [Sideloadly](https://sideloadly.io/).
2. Connect your iPhone SE 3 and install. For an update, keep the same Apple ID and bundle-ID setting, and keep the existing app installed.
3. Keep your already imported cache. For a fresh installation, import `Caches_ipastore.zip` through the game's three-finger double-tap menu.
4. Reopen the game and try a race offline.

**[Simple installation guide, including Sideloadly settings →](INSTALLATION.md)**

Python and Apple build tools are only needed if you choose to [build the IPA yourself](BUILD.md).

## What this fixes

The SE 3's 1334×750 screen made the game select the mostly absent `960x640` GUI assets, even though the imported cache contained their `2048x1536` counterparts. This patch makes the atlas loader and GUI download-list filter use the available high-resolution family together.

**The owner reported successful launch, a race, and an offline cold restart on an iPhone SE 3 running iOS 26.6.1.** This is a one-device result. The release contains the same HD v1 IPA used for that test, including its local diagnostic logger. The `Test` filename identifies this first verified version.

## What is included

- A guarded ARM64 patch and EDS profile transformation.
- A Mac builder that creates a new IPA and preserves the original input.
- A diagnostic control variant for comparing the original resource selection.
- A local logger for asset-file lookups and relevant engine messages.
- 50 emulated ARM64 checks and a native Mac import-hook test.
- English installation, technical and validation documentation.

The Git tree contains source code and documentation. The ready-made IPA is attached separately to the release; the multi-gigabyte cache is linked from upstream. Save files, credentials and raw device logs are excluded.

## Documentation

| Document | Purpose |
|---|---|
| [STATUS.md](STATUS.md) | Working baseline, accepted gaps, exact missing-video record and preservation procedure |
| [ROADMAP.md](ROADMAP.md) | Optional restoration/graphics tasks and criteria for accepting a future change |
| [INSTALLATION.md](INSTALLATION.md) | Download, Sideloadly settings, cache import and offline test |
| [BUILD.md](BUILD.md) | Optional: reproduce the IPA from the original upstream input |
| [TECHNICAL.md](TECHNICAL.md) | Failure mechanism, exact patch locations, diagnostic behavior and format findings |
| [VALIDATION.md](VALIDATION.md) | Device result, baseline evidence, hashes and validation limits |
| [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) | Upstream credits and licenses |

## Scope

The executable and original fallback profile are checked by SHA-256 before building. Re-signed, already patched, encrypted, different-version and unsupported inputs are refused. The patch changes GUI asset selection; it does not change the physical framebuffer, replace cache hashes, restore online services or supply missing optional event assets.

If you already have a working installation, preserve its save and cache and use the same signing account and effective bundle identifier when replacing the app. See the installation guide before attempting an update.

## Credits and license

Built on [Indegosblade/RR3-DevOps](https://github.com/Indegosblade/RR3-DevOps), including its documented EDS transformation. The upstream offline package/importer and cache predate that project; its [provenance document](https://github.com/Indegosblade/RR3-DevOps/blob/main/docs/PROVENANCE.md) credits 有时会很闲 and Flickxie. Import-symbol tracing uses [Meta fishhook](https://github.com/facebook/fishhook).

Original code is MIT licensed. Third-party notices are included separately. Real Racing 3 and its assets remain the property of their respective rights holders. This project is not affiliated with EA, Firemonkeys, Imagination Technologies or Meta.
