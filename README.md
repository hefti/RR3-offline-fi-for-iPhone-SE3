# rr3

**RR3 offline - fix for iPhone SE3** — an exact-build GUI resource-selection fix for Real Racing 3 14.0.1, based on the RR3 DevOps v1.0 Production Quality iOS package.

An iPhone SE (3rd generation) could launch the preserved game but stopped at a **33 MB additional-data download**. Its 1334×750 screen made the game select the mostly absent `960x640` GUI assets, even though the imported cache contained their `2048x1536` counterparts.

This patch makes the atlas loader and GUI download-list filter use the available high-resolution family together. **The owner reported successful launch, a race, and an offline cold restart on an iPhone SE 3 running iOS 26.6.1.** This is a one-device result, not a universal compatibility guarantee.

## Get started

1. Obtain the original [RR3 DevOps Production Quality IPA](https://github.com/Indegosblade/RR3-DevOps/releases/tag/v1.0-4k) and its [asset cache](https://github.com/Indegosblade/RR3-DevOps/releases/tag/v1.0-cache).
2. On a Mac, build your patched IPA from that original input.
3. Re-sign and sideload it with your usual Apple account.
4. Keep or import the matching cache and test offline.

**[Complete build and installation guide → INSTALLATION.md](INSTALLATION.md)**

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python build.py --input "/path/to/RR3-DevOps-v1.0-Production-Quality.ipa"
```

The default output is `dist/RR3-SE3-HD-Test-v1.ipa`. It includes the diagnostic logger used during the successful test. The `Test` filename is retained to identify this first verified version; the project does not claim broader production validation.

## What is included

- A guarded ARM64 patch and EDS profile transformation.
- A Mac builder that creates a new IPA and preserves the original input.
- A diagnostic control variant for comparing the original resource selection.
- A local logger for asset-file lookups and relevant engine messages.
- 50 emulated ARM64 checks and a native Mac import-hook test.
- English installation, technical and validation documentation.

This repository contains **source code and documentation**, not the game IPA, the multi-gigabyte cache, save files, credentials or raw device logs. The matching game/cache must be supplied separately. Building does not install anything on a device.

## Documentation

| Document | Purpose |
|---|---|
| [INSTALLATION.md](INSTALLATION.md) | Inputs, building, signing, cache import, testing and rollback |
| [TECHNICAL.md](TECHNICAL.md) | Failure mechanism, exact patch locations, diagnostic behavior and format findings |
| [VALIDATION.md](VALIDATION.md) | Device result, baseline evidence, hashes and validation limits |
| [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) | Upstream credits and licenses |

## Scope

The executable and original fallback profile are checked by SHA-256 before building. Re-signed, already patched, encrypted, different-version and unsupported inputs are refused. The patch changes GUI asset selection; it does not change the physical framebuffer, replace cache hashes, restore online services or supply missing optional event assets.

If you already have a working installation, preserve its save and cache and use the same signing account and effective bundle identifier when replacing the app. See the installation guide before attempting an update.

## Credits and license

Built on [Indegosblade/RR3-DevOps](https://github.com/Indegosblade/RR3-DevOps), including its documented EDS transformation. The upstream offline package/importer and cache predate that project; its [provenance document](https://github.com/Indegosblade/RR3-DevOps/blob/main/docs/PROVENANCE.md) credits 有时会很闲 and Flickxie. Import-symbol tracing uses [Meta fishhook](https://github.com/facebook/fishhook).

Original code is MIT licensed. Third-party notices are included separately. Real Racing 3 and its assets remain the property of their respective rights holders. This project is not affiliated with EA, Firemonkeys, Imagination Technologies or Meta.
