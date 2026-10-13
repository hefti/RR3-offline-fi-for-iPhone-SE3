# Build from source (optional)

**You do not need Python or these steps to install the ready-made IPA.** Use the [simple installation guide](INSTALLATION.md) for normal installation. This page is for rebuilding or inspecting the fix.

## 1. Download the original build input

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

## 2. Build the HD fix on a Mac

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

## 3. Install your output

Follow [INSTALLATION.md](INSTALLATION.md), using your generated `dist/RR3-SE3-HD-Test-v1.ipa` instead of the downloadable release IPA. The builder never installs anything on an iPhone.
