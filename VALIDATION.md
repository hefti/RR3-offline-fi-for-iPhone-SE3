# Validation record

## Device result

Date: **13 October 2026**. Device: **iPhone SE (3rd generation)**. Reported OS: **iOS 26.6.1**. Game: **Real Racing 3 14.0.1**, using the preserved RR3 DevOps v1.0 package/cache.

The owner first installed the diagnostic control and supplied a startup log. After installing the HD variant, the owner reported that it worked. The owner then reported success following instructions to start a race and fully close/relaunch the game offline.

This is a user-reported functional result on one device. The diagnostic control log was analyzed directly; an HD runtime log or video was not supplied. It does not establish coverage of every car, track, event, iOS release, long-session behavior or device model.

## Baseline log findings

The diagnostic helper loaded successfully and identified the original filter. Runtime values showed a 1334×750 screen, the iPhone fallback profile and iPad feature data, with only 960×640 and 480×320 in the automatic GUI order.

| Nonzero download group | Missing 960×640 files | Logged bytes |
|---|---:|---:|
| Formula 1 group | 24 | 11,124,348 |
| Porsche Mission R event | 8 | 405,385 |
| Weekly time trial | 6 | 997,177 |
| F1 hub common | 2 | 127,640 |
| All or Nothing flashback | 8 | 431,740 |
| Locked quests | 2 | 100,560 |
| Quests v2 | 2 | 128,675 |
| Quest stage backgrounds | 98 | 22,162,277 |
| **Total** | **150** | **35,477,802** |

The total is 33.83 MiB, consistent with the reported integer 33 MB display; the UI's rounding rule was not separately traced. Each group's logged total exactly matched its missing manifest transport sizes plus eight bytes per file. The meaning of that per-file overhead was not independently established.

Concrete download errors named 101 unique small-resolution paths. The complete 150-path set was reconstructed from the eight requested groups and the original manifests, not from 150 separate error records. All 150 direct high-resolution counterparts existed in the Mac archive set. Opening the imported base cache ledger on the phone was observed; the control log did not itself prove every high-resolution file was already present on the device.

Raw logs are excluded because they contain device/container paths and unnecessary engine output. This table preserves the useful aggregate evidence.

## Local checks

- Original IPA and cache ZIP CRC checks passed.
- Original files were unchanged after diagnosis and test-package creation.
- 50 original/patched ARM64 gate cases passed in Unicorn, including preservation of non-GUI behavior.
- A modified input instruction was correctly rejected by the patch guard.
- Native Mac import-hook tests passed for file errors/errno, creation/read behavior, stat output and NSLog formatting/capture.
- Both initial generated IPA ZIPs passed full CRC checks; changed files were verified by readback.
- Main/helper ad hoc code signatures verified locally; the helper had an ARM64 iOS target.
- The Git-ready portable builder was subsequently exercised against the upstream original IPA. A rebuild is not necessarily byte-identical to an earlier IPA because compiler, signature and helper UUID data can vary.

## Reference hashes

| Artifact | SHA-256 |
|---|---|
| Original upstream Production Quality IPA | `f73da1ec286dc36fe1bda8d4ff6c7d67fe844c741a67254d3e05bca38b69548f` |
| Locally repackaged original ARM64 IPA used for the device build | `2ca946f52d7f05212cd8371be2a44157f2447b76de4b699e532feb46bbb03d28` |
| Supplied intact cache ZIP | `96aeb92f1bb6c5ddee73e1a5fb2f4b33ef2e5a5e03fd86380b847cd771a7fc8e` |
| Initial Diagnostic v1 IPA | `0607d6b833b8f1339dd1f7de06a8d3c5f6f3d6b82fc5f0ccb5717dfe17ccdba9` |
| Initial HD v1 IPA reported working | `9462989f1ba03c1130ea589f7b88cff03013177f8813e8075598552392793d65` |

These hashes identify the examined artifacts. The [v1.0-se3 release](https://github.com/hefti/RR3-offline-fix-for-iPhone-SE3/releases/tag/v1.0-se3) provides the exact initial HD v1 IPA reported working, with SHA-256 `9462989f1ba03c1130ea589f7b88cff03013177f8813e8075598552392793d65`. Its embedded build-time metadata predates the owner's device test; the later reported result is recorded above. Full IPAs and the cache are not stored in the Git tree. Current local rebuild hashes are written to `dist/SHA256SUMS.txt`.
