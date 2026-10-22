# Fallout New Vegas on Steam: Prepare the Game for Mods

Before you install any Fallout: New Vegas mods on the Steam version, the Viva New Vegas modding guide wants a clean copy of the game in a safe folder, a few Windows checks and one first launch. This post walks through that preparation for a Steam copy, following the guide's own Setup page. It does not cover the mods themselves.

*Checked October 22, 2026 against the Viva New Vegas guide's Introduction, Setup and Wabbajack pages, and PC Gamer's New Vegas guide. The guide says to read everything and not skip steps. Nothing here was tested in the game.*

## What your copy needs

The guide's [Introduction](https://vivanewvegas.moddinglinked.com/intro) lists these requirements:

- An English copy of the game with all DLCs from Steam, GOG or the Epic Games Store. Microsoft Store versions are not supported.
- The Polish-Czech-Russian version works as long as the game itself is in English. The German release is a "No Gore" version that is also incompatible with xNVSE, and Steam owners can use DepotDownloader to get the international executable.
- At least 19GB of free space including the game, or 17GB if you delete all the downloads.
- Windows 10 or higher, 64-bit. Customized or LTSC installations are not supported.
- A text editor, an archiving tool, the latest GPU drivers and a Nexus Mods account.

The guide says the game is far more CPU-intensive than GPU-intensive, and that an SSD will drastically improve loading times and decrease stuttering. [PC Gamer's guide](https://www.pcgamer.com/fallout-new-vegas-guide-tips-best-experience/) agrees on the edition: it says to get the Ultimate Edition from Steam, GOG or Epic if you plan to mod, and to skip the Game Pass and Microsoft Store versions because they do not play nicely with the Script Extender many mods use.

## Windows preparation

From the [Setup page](https://vivanewvegas.moddinglinked.com/setup.html):

1. **Update the Visual C++ Redistributables.** The guide has you update everything in the Microsoft Store, which also updates Winget, then run a set of Winget commands in an administrator Command Prompt and restart. Copy the command from the guide itself rather than retyping it. It says a missing or outdated version means an immediate crash.
2. **Show file extensions** in File Explorer, because the guide refers to `.exe`, `.dll` and `.esp` files.
3. **Check Mandatory ASLR is off.** In Windows Security, open App and browser control, then Exploit protection settings, and make sure "Force randomization for images (Mandatory ASLR)" is on its default of Off. The guide also describes a per-program exception for `FalloutNV.exe`.

## Choose a safe install location

The guide says to avoid default Windows folders such as Program Files, Program Files x86, the Desktop and Documents. Users lack write access to Program Files, and OneDrive often manages the Desktop and Documents folders. Its example of a safe location is `C:\Games`.

## Clean up any old install (Steam)

If you installed the game before, the guide has you:

1. Uninstall Fallout: New Vegas in Steam through Manage, then Uninstall.
2. Delete any leftover `Fallout New Vegas` folder in `Steam\steamapps\common`.
3. Delete all INI files in `Documents\My Games\FalloutNV`.

## Install to a new Steam library

If your Steam is in Program Files, the guide has you create a library elsewhere using the [Steam Library Setup Tool](https://github.com/LostDragonist/steam-library-setup-tool/releases):

1. Exit Steam completely, including the system tray.
2. Run the tool, add a row, and type a path such as `C:\Games\Steam`.
3. Accept, and confirm when asked to create the folder.
4. Open Steam, select Fallout: New Vegas and choose Install, then pick the new library folder under "Install to".
5. If the library does not appear, restart your PC.

## Generate fresh INI files

The guide's last step before modding is to launch the game once from Steam. Click OK on both "Detecting Video Hardware" pop-ups, then OK and Exit. If no pop-ups appear, delete the INI files in `Documents\My Games\FalloutNV` and try again.

The guide's "Root" folder for a Steam copy is `Steam\steamapps\common\Fallout New Vegas` and its "Data" folder is the `Data` folder inside it. You will see both names often in the rest of the guide.

## Wabbajack or manual

The guide offers a [Wabbajack page](https://vivanewvegas.moddinglinked.com/wabbajack.html) for automated installation. That page says only Steam (Global) and GOG copies are supported by the Wabbajack version. If you use Wabbajack, the Setup page tells you to return to the Wabbajack page's Installation section after this preparation. Otherwise you continue through the manual pages, starting with Mod Organizer 2. PC Gamer's guide also names Viva New Vegas as its top recommended mod pack and says, in an update from December 2025, that it is once again available through Wabbajack.

Our [modding guide](https://frontbuffer.net/gaming/fallout-series_guide/) explains what Viva New Vegas is and how its two sections differ.

---
Sources:
- [Introduction, Viva New Vegas](https://vivanewvegas.moddinglinked.com/intro)
- [Initial Setup, Viva New Vegas](https://vivanewvegas.moddinglinked.com/setup.html)
- [Wabbajack, Viva New Vegas](https://vivanewvegas.moddinglinked.com/wabbajack.html)
- [Steam Library Setup Tool releases, GitHub](https://github.com/LostDragonist/steam-library-setup-tool/releases)
- [How to have the best Fallout New Vegas experience today, PC Gamer](https://www.pcgamer.com/fallout-new-vegas-guide-tips-best-experience/)
