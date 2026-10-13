# Install on iPhone SE 3

**No Python, Xcode or compiling is needed to install the ready-made IPA.** You need your iPhone SE 3, a computer with [Sideloadly](https://sideloadly.io/), a USB cable and your Apple ID.

## 1. Download the fixed IPA

**[Download RR3-SE3-HD-Test-v1.ipa](https://github.com/hefti/RR3-offline-fix-for-iPhone-SE3/releases/download/v1.0-se3/RR3-SE3-HD-Test-v1.ipa)** — about 1.37 GB.

On the [release page](https://github.com/hefti/RR3-offline-fix-for-iPhone-SE3/releases/tag/v1.0-se3), choose this `.ipa` under **Assets**. The automatically generated “Source code” ZIP is for developers.

> **Installation base:** [RR3 DevOps v1.0 Production Quality, game version 14.0.1](https://github.com/Indegosblade/RR3-DevOps/releases/tag/v1.0-4k). The fixed IPA already includes this base and our SE 3 fix. Sideload it directly. The original upstream IPA is only needed for the optional [build-from-source workflow](BUILD.md).

**Already have the game and cache?** Back up your save/data, leave the app installed, and install this IPA as an update. Use the same Apple ID and bundle-ID setting as before. Skip step 3 if the cache is already imported.

## 2. Install with Sideloadly

1. Open [Sideloadly](https://sideloadly.io/) on your computer.
2. Connect and unlock your iPhone. Select it in **iDevice**.
3. Drag `RR3-SE3-HD-Test-v1.ipa` into Sideloadly.
4. Enter or select your Apple ID.
5. Open **Advanced Options** and use these settings:

| Sideloadly option | What to choose |
|---|---|
| **Use automatic bundle ID** | Keep the default for a new install. For an update, use the same setting and Apple ID as before; if you previously used a custom ID, keep that exact ID. |
| **Enable File Sharing** | Enable it so diagnostic logs can be retrieved if needed. |
| **Inject dylibs/frameworks** | Leave off. The fix and logger are already included in the IPA. |
| App name/version, custom entitlements, older-iOS and device compatibility options | Leave at their defaults unless your existing signing setup requires otherwise. |

Click **Start**, wait until installation finishes, and complete any account or iPhone trust/developer-mode steps requested by Sideloadly or iOS. Launch the installed **RR3 SE3 HD Test** app.

**If you are updating:** do not delete the old app to fix a signing error. Deleting it can remove your save and imported cache. Check the signing account and bundle ID first.

## 3. Import the cache — only if needed

**If the matching cache is already imported, skip to step 4.**

The game needs the separate [RR3 DevOps v1.0 asset cache](https://github.com/Indegosblade/RR3-DevOps/releases/tag/v1.0-cache). If you already have the complete `Caches_ipastore.zip`, use it and skip the downloads below.

For a fresh installation, download all three parts into the same folder on your computer:

| File | Download |
|---|---|
| Cache part 1 | [part00](https://github.com/Indegosblade/RR3-DevOps/releases/download/v1.0-cache/RR3-DevOps-v1.0-Asset-Cache.zip.part00) |
| Cache part 2 | [part01](https://github.com/Indegosblade/RR3-DevOps/releases/download/v1.0-cache/RR3-DevOps-v1.0-Asset-Cache.zip.part01) |
| Cache part 3 | [part02](https://github.com/Indegosblade/RR3-DevOps/releases/download/v1.0-cache/RR3-DevOps-v1.0-Asset-Cache.zip.part02) |

Verify the parts against the upstream [checksums](https://github.com/Indegosblade/RR3-DevOps/blob/main/SHA256SUMS.txt). Together they form a roughly 5.52 GB ZIP; the unpacked cache needs about 8.26 GB, plus room for the app and import process.

<details>
<summary><strong>Only have the three parts? Join them into one ZIP</strong></summary>

On a Mac, if all three parts are in **Downloads**, open **Terminal** and paste this once. It joins the parts; it does not build the game or need Python. If a completed ZIP already exists, it leaves it untouched.

```sh
cd ~/Downloads
if [ ! -e Caches_ipastore.zip ]; then
  cat RR3-DevOps-v1.0-Asset-Cache.zip.part00 \
      RR3-DevOps-v1.0-Asset-Cache.zip.part01 \
      RR3-DevOps-v1.0-Asset-Cache.zip.part02 > Caches_ipastore.zip
fi
```

For Windows joining instructions, see the [upstream cache release](https://github.com/Indegosblade/RR3-DevOps/releases/tag/v1.0-cache).

</details>

Then import the completed ZIP:

1. Transfer `Caches_ipastore.zip` to the iPhone, for example with AirDrop, and save it somewhere you can find in **Files**. Keep it as a ZIP.
2. Open **RR3 SE3 HD Test**. Tap the screen twice with **three fingers at the same time** to open the existing cache importer.
3. Choose its **first import option**, then select `Caches_ipastore.zip`.
4. Wait for the import to finish. Close the game completely and reopen it.

The importer comes from the upstream preserved package. Its [original deployment guide](https://github.com/Indegosblade/RR3-DevOps/blob/main/docs/INSTALLATION.md) provides additional details.

## 4. Check that it works

Open the main menu and garage, start a race, then close the game completely and reopen it with the internet disconnected. Check that menus and touch targets look correct.

These steps were reported working on the tested SE 3. Some optional events may still need assets absent from the preserved cache.

## If something goes wrong

| Problem | Next step |
|---|---|
| Still asks for 33 MB | Confirm you installed **RR3 SE3 HD Test** and that the cache is imported into that app. |
| Signing/install error | Check Sideloadly's error. For an update, keep the same Apple ID and bundle ID; leave the existing game installed. |
| Cache importer cannot find the ZIP | Save the complete ZIP in Files first. Select the joined ZIP, not one of the three parts. |
| Crash or incorrect menus | Keep the latest log and restore your original IPA using the same signing setup and your backup. |

For a useful log, leave the game open for about two minutes if possible. Retrieve the newest file from the app's shared **RR3-Diagnostics** folder through Finder file sharing or Files. Logs stay local; review and redact them before sharing publicly. See [technical diagnostics](TECHNICAL.md#reading-the-diagnostic-log) for interpretation.

Re-signing/refresh is handled by your Apple account and sideloading tool. Keep your original IPA and backup for rollback.

Want to reproduce the patch? The separate [build guide](BUILD.md) contains the Python commands; they are optional for installation.
