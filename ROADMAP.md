# Optional restoration and improvement roadmap

Updated: **13 October 2026**. The goal is to preserve the owner's working installation and make further improvements only when they provide a concrete benefit. See [STATUS.md](STATUS.md) for the baseline and accepted gaps.

## Priorities

| Priority | Work | Tracking / completion criteria |
|---|---|---|
| First, before any future experiment | Preserve working package, cache and save; record provenance and rollback setup | Follow [preservation procedure](STATUS.md#preserve-the-working-setup). A fresh backup has not been verified in this session. |
| Optional restoration | Find the original `SpeedRush_TV_commercial.mp4` | [Issue #1](https://github.com/hefti/RR3-offline-fix-for-iPhone-SE3/issues/1): compatible provenance, size/checksum verification and a separate-copy test before adoption |
| Optional cosmetic improvement | Identify and investigate the accepted black backgrounds | [Issue #2](https://github.com/hefti/RR3-offline-fix-for-iPhone-SE3/issues/2): exact screen/reproduction evidence first; preserve the baseline |
| Later, if useful | Reconstruct a missing asset or improve graphics | Extend the relevant issue once the target and expected benefit are known. Prefer original compatible content; isolate texture/atlas experiments and validate layout/touch behavior. |

The current omissions do not require a new release. A future crash, unusable screen, blocked race or save problem should get its own issue with reproduction details; do not infer it from the inventory count alone.

## Accepting a future change

For a candidate that changes game/package/cache behavior, record the changed files, input/output identity and reason for the change. Check on the intended device:

- The affected screen/event and its expected behavior.
- Main menu/garage, a race and offline cold restart.
- Layout/touch targets if a graphical change is involved.
- Save/cache continuity and a usable rollback copy.

Record who performed each check, the device/OS/package/cache versions and the result. A code-level check or successful build does not establish game/device validation. Do not present a rebuilt or modified IPA as the previously working artifact without new evidence.

## GitHub organization

The repository stores source, reproducible build instructions, status/evidence and the optional task list. The two issues are sufficient for the current scope.

On 13 October 2026, the [public repository Projects page](https://github.com/hefti/RR3-offline-fix-for-iPhone-SE3/projects) showed no linked projects. This was a signed-out view; private projects were not inspected. No new Project was created because it would duplicate this small issue list. Reconsider a board when several active work streams, milestones or contributors need shared prioritization; link the existing issues rather than duplicating their contents.
