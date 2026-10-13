# Build and installation

## 1. Prepare the inputs

You need a Mac with Apple Command Line Tools, Python 3 (3.13 was tested), enough disk space for the original and generated IPA, an iPhone SE 3, and your normal sideloading account/tool. The original cache is about 5.5 GB as a ZIP and about 8.26 GB unpacked; allow additional free space for import and installation.

Download the original `RR3-DevOps-v1.0-Production-Quality.ipa` from the upstream [v1.0-4k release](https://github.com/Indegosblade/RR3-DevOps/releases/tag/v1.0-4k). Its published SHA-256, also verified locally, is:

```text
f73da1ec286dc36fe1bda8d4ff6c7d67fe844c741a67254d3e05bca38b69548f
```

Use the original package before sideloading/re-signing. Do not use an already installed/exported or already patched IPA as the builder input. The builder validates the exact executable and EDS bytes, not just a version string. A locally repackaged ARM64 archive with identical checked contents is also accepted.

For a new installation, obtain all three asset-cache parts from the upstream [v1.0-cache release](https://github.com/Indegosblade/RR3-DevOps/releases/tag/v1.0-cache). Verify the parts against the upstream [checksums](https://github.com/Indegosblade/RR3-DevOps/blob/main/SHA256SUMS.txt), then join them in their original order:

```sh
cat RR3-DevOps-v1.0-Asset-Cache.zip.part00 \
    RR3-DevOps-v1.0-Asset-Cache.zip.part01 \
    RR3-DevOps-v1.0-Asset-Cache.zip.part02 > Caches_ipastore.zip
```

Keep the resulting ZIP intact for the in-app importer. If that cache is already imported in your working installation, keep it; an update does not automatically require another import. The upstream [deployment guide](https://github.com/Indegosblade/RR3-DevOps/blob/main/docs/INSTALLATION.md) describes the original importer workflow.

## 2. Build the HD fix

Clone or download this repository, open a terminal in its folder, and run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python build.py \
  --input "/path/to/RR3-DevOps-v1.0-Production-Quality.ipa"
```

The output is:

```text
dist/RR3-SE3-HD-Test-v1.ipa
dist/RR3-SE3-HD-Test-v1.ipa.report.json
dist/SHA256SUMS.txt
```

The builder runs native and emulated checks, compiles the helper, verifies local code signatures, validates the completed ZIP, and checks that the input hash is unchanged. Existing output IPAs are never overwritten. Use a different `--output-dir` for another build.

For both the unmodified-selection diagnostic control and the HD fix:

```sh
.venv/bin/python build.py --input "/path/to/original.ipa" --variant both
```

To validate the input and run tests without producing an IPA:

```sh
.venv/bin/python build.py --input "/path/to/original.ipa" --check-only
```

The tested helper build uses public Darwin/CoreFoundation APIs with macOS SDK headers and explicit iOS linker interface descriptions. It produces an ARM64 iOS 13+ Mach-O; a complete iOS SDK is not required for this workflow. This specific technique was exercised during the successful device test. It is not a substitute for testing a new compiler or device combination.

## 3. Preserve an existing installation

Before replacing an installed copy, back up the iPhone and preserve the game's save/data. Keep the original IPA and cache for rollback.

Use the same Apple ID and **effective bundle identifier** as the existing installation. If the original sideload used automatic bundle IDs, keep that setting with the same account. If it used a custom identifier, use the same custom value. The package's base identifier is `com.ea.realracing3.inc`, but a signing tool may transform it.

Install as an update. Do not delete the existing game just to make installation proceed: deleting it can remove its save and imported cache. Stop and resolve an identifier or signing mismatch first. Matching identifiers can preserve the container, but are not a replacement for a backup.

## 4. Re-sign and sideload

The generated IPA contains locally verified **ad hoc** signatures. These are not Apple account/device installation authorization. Re-sign through [Sideloadly](https://sideloadly.io/) or your established sideloading workflow.

In Sideloadly:

1. Connect/unlock the iPhone and select it.
2. Load `RR3-SE3-HD-Test-v1.ipa`.
3. Select the same Apple account used for the existing installation, if applicable.
4. Keep the matching bundle-ID setting described above.
5. Enable File Sharing so the diagnostic logs are accessible. The IPA already requests Documents sharing.
6. Leave additional tweak injection off: `RR3Diagnostics.dylib` is already embedded and referenced.
7. Leave app-name/version overrides, custom entitlements and compatibility overrides unchanged unless your established signing workflow requires them.
8. Start signing and installation. Complete any normal device/account trust step requested by iOS or your signing tool.

No optional RR3 DevOps overlay injection is needed for this patch. Signing expiration/refresh remains governed by your Apple account and sideloading tool.

## 5. Import the cache, if needed

For a fresh installation, place the intact `Caches_ipastore.zip` somewhere accessible from the iPhone Files app. In the preserved game's importer, use a three-finger double-tap, choose the cache ZIP, and wait for completion. Force-quit the app and reopen it afterward. This importer is inherited from the upstream package, not implemented here.

Do not repeat a completed import merely because you updated the IPA. If required data is absent, use the logs to check the actual paths first.

## 6. Verify offline operation

Check launch and entry to the main menu, garage access, a race, and a full app close/relaunch without an internet connection. Also check image scale, clipping and touch targets.

Those basic steps were reported working on the tested SE 3. Optional events whose high-resolution assets are absent from the original cache may still request downloads; this patch does not generate missing content or restore servers.

## 7. Collect diagnostics

Logs are written inside the app's own container:

```text
Documents/RR3-Diagnostics/session-<timestamp>-<pid>.log
```

Retrieve them from the app's shared documents through Files or Finder file sharing. If startup fails or requests data, leave the app open for approximately two minutes if possible and collect the latest log.

`MISSING_OR_ERROR` means a failed filesystem probe, not necessarily a missing mandatory asset. Interpret it alongside the `ENGINE` download messages. The HD log should identify its detour in the `BUILD` record. The actual atlas lookups should use the high-resolution family; the old `Res order` enumeration alone is not conclusive because the explicit override bypasses that lookup order.

Logs stay local, with an 8 MiB limit per session. The logger attempts to omit credential-related engine messages, but inspect and redact a log before posting it publicly. This repository intentionally excludes the original raw device log.

## Troubleshooting and rollback

- **Unsupported input:** obtain the exact upstream original, not a re-signed or different-version package. The error is deliberate.
- **Output already exists:** choose a new output directory; the builder will not overwrite it.
- **33 MB remains:** check that the HD IPA was installed, the log identifies the HD detour, and the existing cache is in the app's active container. Then inspect the requested file names.
- **Crash or incorrect GUI:** preserve the log and restore the known original package with the same signing identity, following your normal backup/restore procedure.
- **No log:** check that the new app launched and that its Documents sharing is accessible. A crash before the constructor runs may require a device crash report instead.

Keep your original package and backup. The patch changes live code/profile selection in the app package, not a saved graphics preference; normal game execution can still update its own files.
