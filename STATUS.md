# Current status and preservation

Updated: **17 October 2026**.

## Recovered after iOS 26.7.1 update

The owner reported that updating only iOS from 26.6.1 to 26.7.1 was followed by a **661 MB** download stall. The supplied log still detected the HD fix but could not open the imported base-cache ledger. **Re-importing the existing matching cache ZIP through the blue folder menu resolved the problem, according to the owner.** See the [step-by-step recovery and screenshot](docs/cache-recovery.md) and [validation record](VALIDATION.md).

The existing `v1.0-se3` IPA remains the reference package. This recovery needed no new IPA or code change. The exact reason the cache/ledger became unavailable is unproven; no post-recovery log or separate new race/offline-start confirmation was supplied.

## Working baseline

The owner reports that the current RR3 installation works. They mention perhaps **1–2 black backgrounds**, which they consider acceptable. This is the baseline to preserve while optional restoration work is considered.

The original baseline records Real Racing 3 **14.0.1**, the RR3 DevOps v1.0 package/cache and an **iPhone SE (3rd generation)** running reported **iOS 26.6.1**. Its earlier validation record describes owner-reported launch, a race and an offline cold restart, followed by acceptance of the occasional black backgrounds. The later iOS 26.7.1 incident and recovery are recorded above. See [VALIDATION.md](VALIDATION.md) for the evidence and its limits.

Reference package: [`v1.0-se3` release](https://github.com/hefti/RR3-offline-fix-for-iPhone-SE3/releases/tag/v1.0-se3), asset `RR3-SE3-HD-Test-v1.ipa`. The recorded SHA-256 before re-signing is:

```text
9462989f1ba03c1130ea589f7b88cff03013177f8813e8075598552392793d65
```

This checksum is also listed by the release metadata inspected during this review. The release asset was not downloaded or rehashed here. Re-signing changes package bytes; this checksum does not identify an exported, re-signed installation. No new IPA, release or game-file change accompanies this status update.

## Known and accepted gaps

| Finding | Evidence | Current disposition |
|---|---|---|
| 24,791 present out of 24,792 listed resources | Earlier diagnostic count, carried forward from the conversation and existing technical record; no new scan | Preserve as historical inventory evidence, not proof that every screen/event is complete |
| Missing `SpeedRush_TV_commercial.mp4` | Earlier diagnosis and exact record supplied by the owner | Optional original-content recovery, [issue #1](https://github.com/hefti/RR3-offline-fix-for-iPhone-SE3/issues/1) |
| Perhaps 1–2 black backgrounds | Latest owner feedback; exact screens/cause unknown | Accepted cosmetic limitation; optional investigation, [issue #2](https://github.com/hefti/RR3-offline-fix-for-iPhone-SE3/issues/2) |

The missing video has **not** been established as the cause of the black backgrounds or as a current gameplay blocker. The earlier 33 MB download stall and its GUI-family fix are documented separately in [TECHNICAL.md](TECHNICAL.md).

## Missing promotional video

Referencing list: `asset_list_quest_speedrush_assets.txt`.

Exact record supplied by the owner:

```text
/SpeedRush_TV_commercial.mp4 7f9560c4abf3665fd4bd62e01aa9f689 6925760 6925760
```

Recorded hash: `7f9560c4abf3665fd4bd62e01aa9f689`. Both recorded size fields are **6,925,760 bytes**. These are search/verification references, not a checksum computed from a recovered file. The source manifest and cache are not present in this repository and were not independently re-examined during this review.

When an original candidate becomes available, record its source and matching game/cache version, verify the size and checksum in the representation expected by the manifest, then test it in a separate copy. The earlier cache investigation found transport/stored-file checksum differences for other resources; a raw stored-file mismatch alone is not sufficient to declare corruption. Do not rewrite manifest hashes or remove entries to hide a missing resource.

## Preserve the working setup

This is the procedure for future work; completion of a fresh backup is **not** claimed here.

1. Keep the currently working IPA, original cache archive and a backup of save/app data outside the repository. Record package/cache provenance, versions and checksums where available, plus the effective bundle ID/signing setup needed to retain the save. Keep credentials and private logs out of GitHub.
2. Keep the working phone installation and imported cache in place. A missing optional video or accepted black background alone is not a reason to delete/reinstall the app, import the cache again or replace working assets.
3. Use a separate source branch and separate package/cache copies for experiments. Preserve original input bytes and use a new output location. The existing builder already refuses to overwrite output IPAs.
4. Promote a candidate only after relevant device checks and a documented rollback path. A documentation change needs no device installation. If a device update is actually needed, retain the signing account/effective bundle ID and follow [INSTALLATION.md](INSTALLATION.md).

## What was checked in the 13 October documentation review

The repository source/documentation, existing issues, public Projects page and release metadata were inspected. Two optional issues were created and the documentation was updated. No game/device test, build, fresh inventory scan, file recovery, backup or cache modification was performed. Historical test results remain attributed to their existing record and the owner.

For the 17 October update, the supplied incident log was analyzed and the owner's recovery confirmation was recorded. The loading-screen screenshot is included with permission. No code, release asset or original input was changed.

For priorities and future acceptance criteria, see [ROADMAP.md](ROADMAP.md).
