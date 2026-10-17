# Stuck at 0 / 661 MB after an iOS update

**Confirmed recovery on an iPhone SE 3: re-import the existing `Caches_ipastore.zip` through the blue folder menu, then fully close and reopen the game.** No new IPA, Sideloadly installation or Python is needed for this recovery.

## What happened

The previously working installation started asking for **661 MB** after the owner updated **iOS 26.6.1 to 26.7.1**. The owner reported that only iOS was updated: the game was not reinstalled or re-signed.

![Real Racing 3 stopped at 0 / 661 MB after the reported iOS update](images/661mb-download.jpeg)

*Owner-supplied screenshot, published with permission. The blue folder button at the upper right opens the importer.*

## Fix: import the cache again

Keep the installed game and your save. Use the same complete **`Caches_ipastore.zip`** that worked with this package before. If you already have it, there is no need to download the cache again. If you need a replacement, use the matching [RR3 DevOps v1.0 cache](https://github.com/Indegosblade/RR3-DevOps/releases/tag/v1.0-cache); [joining its parts is explained in the installation guide](../INSTALLATION.md#3-import-the-cache--only-if-needed).

1. Put the complete ZIP in **Files** on the iPhone. You can AirDrop it from the Mac; a USB cable is not needed for that transfer. Leave the archive zipped.
2. Open the game and tap the **blue folder icon** at the upper right of the loading screen.
3. In the Chinese menu, select the **first green row: `导入数据包` — Import data package**.
4. Select **`Caches_ipastore.zip`** and wait until the import finishes. Select the complete ZIP, not a `.part00`, `.part01` or `.part02` file.
5. Fully close the game from the app switcher and open it again.
6. Check the main menu and try a race. Then fully close and reopen it with the internet disconnected to check offline startup.

**Choose the data-package option, not the save-import option:**

| Menu label | Meaning | Use for this fix? |
|---|---|---|
| `导入数据包` | Import data package | **Yes — first green row** |
| `导入应用存档` | Import app save | No — this is a different operation |
| `导出应用存档` | Export app save | No |

This menu belongs to the preserved package's file assistant. It is separate from the optional RR3 DevOps button.

**Result:** after receiving these instructions, the owner confirmed that this resolved the problem. A new post-recovery log and a separate confirmation of the race/offline checks were not supplied for this incident. The earlier race and offline-start result remains recorded under the original iOS 26.6.1 test in [VALIDATION.md](../VALIDATION.md).

## What the diagnostic log showed

The startup log supplied for this incident still showed the SE 3 HD fix running:

| Observation | Interpretation |
|---|---|
| `GUI filter site=17e60b37; HD detour present` | The patched GUI filter was still detected. |
| `res/eds/iPhone14,6.plist` probe succeeded; `GUI_ATLAS_OVERRIDE` was `2048x1536` | The SE 3 profile and high-resolution GUI selection were still active. |
| 13 distinct high-resolution GUI paths had successful file probes | Some HD GUI resources were present at the probed paths. |
| `Library/Caches/asset_list_base.txtCache.txt` failed to open with `errno=2` (`ENOENT`) | The imported base-cache ledger was missing at the path the game tried to open. The earlier control log had opened this ledger successfully. |
| `nBytesToDownload = 693986702` | About 661.84 MiB was requested, consistent with the screen's 661 MB label. The UI's rounding rule was not traced. |

This supports a missing or unavailable imported cache/ledger rather than loss of the SE 3 GUI patch. **It does not prove that iOS deleted the entire cache or establish exactly why the file became unavailable.** The log covers recorded file operations, not a complete filesystem inventory. The iOS update is the reported trigger in this one-device case; this is not evidence that every iOS update causes it.

The raw log remains private because it contains device/container paths. The table above retains the useful evidence without those identifiers.

## If it happens again

Keep a copy of the matching cache ZIP outside the app so it can be imported again. Re-importing restored this installation; it is a recovery procedure, not a change that guarantees the cache will persist through future updates.

If importing does not resolve it, keep the app installed and retain the newest **RR3-Diagnostics** log for analysis. Review and redact it before sharing. See [diagnostic instructions](../TECHNICAL.md#reading-the-diagnostic-log). This case did not require replacing the IPA, rebuilding the patch or changing asset hashes.

Incident and owner-confirmed recovery recorded: **17 October 2026**. Device: **iPhone SE (3rd generation)**. Game: **14.0.1**, existing **v1.0-se3** package with the matching preserved cache.
