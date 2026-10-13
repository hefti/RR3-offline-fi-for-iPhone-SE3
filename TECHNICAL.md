# Technical description

## Failure mechanism

The preserved cache's base ledger listed 24,792 paths, with only one missing promotional video. That did not establish coverage for every device-specific GUI family. The archive had 2,758 high-resolution GUI files and only four streamed `960x640` files; the IPA also contained a separate bundled GUI set.

The diagnostic SE 3 run showed `Res base: 1334x750` and only `gui_assets/960x640/` and `gui_assets/480x320/` in the automatic resolution order. The iPad-derived fallback settings were present, yet screen-dependent resource selection still excluded the larger family.

Eight nonzero download groups accounted for 150 missing small-resolution files and 35,477,802 download bytes (33.83 MiB). Every corresponding high-resolution path existed in the supplied archive set. This explains why a resolution-selection fix could remove this startup block without converting thousands of textures.

## Supported build and guards

| Check | Required value |
|---|---|
| Game version | 14.0.1 |
| Main executable UUID | `06ed5b50c44c3b69a5840701b8a88451` |
| Main executable SHA-256 | `066a4d304a35bcfbd87847189fbbb2af8e9bac0ca7a02d38ac420952d0701378` |
| Original fallback EDS SHA-256 | `dfd454078eb77509ef3a48ded309aece63cc03338775a8aea712e11c3a9cb19a` |

In addition, the original instruction sequence, zero-filled cave, header room and profile fields are checked. All addresses below belong to this exact executable, before ASLR. File offsets are not portable to another binary.

## Two coordinated changes

**Atlas selection:** decrypt `res/eds/iPhone.plist` using the upstream modified-RC4 algorithm, change only `GUI_ATLAS_OVERRIDE` from an empty string to `2048x1536`, then re-encrypt it. Add a matching `iPhone14,6.plist` for the SE 3 while retaining the internal `PLIST_IDENTIFIER=iPad6,8`. The original layout, `GUI_IMAGE_AUTO_SCALE` value and 3D settings are preserved.

**Download selection:** the function at VA `0x100680a18` recognizes both `/gui_assets/%dx%d/` and `/images_%dx%d/`. Its gate normally loads screen-derived thresholds, then retains a larger admitted resource variant for a canonical path. The patch branches from file offset `0x680b24` into verified unused executable-segment padding at `0x3800`.

The 40-byte leaf stub reproduces the original loads and stack read. Only when the first GUI parse returned two dimensions (`w23 == 2`) does it substitute `w8=2048` and `w9=1536`. Otherwise, the original thresholds remain. It branches back to VA `0x100680b38`, allowing the original comparison and selection algorithm to continue. No new call frame is needed.

The physical framebuffer and the global screen-derived values are not rewritten. The original non-GUI `/images_…/` behavior, asset verification and cache metadata are retained. This is a GUI target-family change, not a blanket download bypass or a framebuffer-resolution patch.

## Packaging and signing

The builder operates on a new ZIP, copying unchanged local ZIP records without recompressing their contents. It updates the main executable, `Info.plist`, and HD profiles; adds the diagnostic helper and build metadata; and removes the stale root app resource seal. A fresh account-authorized resource seal must be generated when sideloading.

The inherited `AppData.dylib` and `iPASTORERR3Fix.dylib` are preserved. The app display name distinguishes HD and diagnostic variants. Documents sharing is enabled for log retrieval. Neither the builder nor its tests connect to an iPhone.

## Diagnostic helper

The helper checks the game's UUID before using its known global addresses. It uses fishhook only on the main executable's imports: `fopen`, `open`, `access`, `stat`, `lstat` and `NSLog`. The existing engine text-log gate is enabled; no game cheat/developer controls are enabled. A two-minute worker samples the original screen-derived asset thresholds.

Relevant file probes and engine messages are written to the app's Documents directory, capped at 8 MiB per session. Original filesystem results/errno and system logging are preserved. The helper does not modify cache/save data or upload logs. Ordinary game code can still write its own files.

The HD target is local to the list-filter stub, so the logger can correctly continue to show global thresholds of `1334x750`. Likewise, automatic `Res order` output can still list smaller families even when the override directs actual atlas loads to `2048x1536`.

## Reading the diagnostic log

Logs are stored at `Documents/RR3-Diagnostics/session-<timestamp>-<pid>.log` inside the app's container. Retrieve the newest file through Files or Finder file sharing after approximately two minutes of startup, if possible. A crash before the helper constructor runs may require a device crash report instead.

`MISSING_OR_ERROR` records a failed filesystem probe; it does not by itself establish that a mandatory asset is missing. Read it alongside the `ENGINE` download messages. An HD build should identify its detour in the `BUILD` record and use the high-resolution family for actual atlas lookups. The old `Res order` output alone is not conclusive.

The limit is 8 MiB per session. The logger attempts to omit credential-related engine messages, but inspect and redact a log before publishing it.

## Texture investigation

GUI `.pvr.z` files had a four-byte decompressed-size prefix, a zlib stream and a legacy 52-byte PVR v2 header. The examined set included raw RGBA8888/16-bit/RGB888 and PVRTC 2/4 bpp formats. The `.ios.atlas` files were XML with named image dimensions and page/position records.

Local probes demonstrated RGBA sprite extraction, resizing, repacking and pixel-exact encode/decode, plus PVRTC decoding/resizing. Atlas placement and some image dimensions differed across resolution families, so whole-page scaling was not sufficient. Of 1,761 missing small atlas families, 1,336 had complete large source families and 425 did not. This conversion work was diagnostic; generated substitute textures are not part of the successful patch.

The original cache's stored-file bytes also did not always share the transport hash listed in manifests. All 8,733 raw-MD5 differences occurred where transport/storage sizes differed and the stored size matched. This is not evidence that 8,733 files were corrupt, and the fix does not rewrite their hashes.

See [VALIDATION.md](VALIDATION.md) for the evidence and the limits of the device claim.
