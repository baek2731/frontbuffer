# How to install IKEA-themed mods for Skyrim Anniversary Edition

The Skyrim modding community has produced IKEA-themed furniture mods — "IKEA Home Furnishings" and "IKEA - A Nordic Home" are the two most common — that add Scandinavian-style furniture to the game. Installing them on Anniversary Edition (AE) requires a few extra steps compared to older Special Edition installs due to executable version changes.

---

## Why AE Modding Is Different

Skyrim Anniversary Edition runs on executable version 1.6.x. Many older mods were built for Special Edition 1.5.97. Mods that rely on SKSE64 or compiled plugins need versions matched to 1.6.x. Checking compatibility before installing prevents crashes.

---

## Step 1: Back Up Your Game

Copy the entire Skyrim Special Edition folder (Steam → steamapps → common → Skyrim Special Edition) to a safe location before installing any mods. If something breaks, you can restore from this copy.

---

## Step 2: Install a Mod Manager

Use Mod Organizer 2 (MO2) or Vortex. Both create a virtual file system that keeps your game's Data folder clean and makes uninstalling or reordering mods straightforward. Manual installation directly into the Data folder is harder to troubleshoot and not recommended for multi-mod setups.

---

## Step 3: Install SKSE64 (if required)

Check the IKEA mod's requirements page on Nexus Mods. If it lists SKSE64 as a dependency, download the version that matches your AE executable from skse.silverlock.org. The version number must match exactly — a mismatch causes crashes on launch.

---

## Step 4: Install the Mod

1. Download the mod from its Nexus Mods page.
2. In your mod manager, use "Install from file" and select the downloaded archive.
3. Activate the mod and let the manager deploy it.
4. Check the mod's description page for load order notes — some furniture mods need to load after specific master files.

---

## Step 5: In-Game Activation

IKEA-themed mods typically add furniture via crafting recipes at a workbench, or through console commands. Check the mod's Nexus page for specifics. To find items via console: open the console with the tilde key, type `help IKEA 4`, and use `player.additem [item ID] 1` to spawn them.

---

## Troubleshooting

**Crashes on load:** Check that SKSE64 version matches your AE executable. Run LOOT (loot.github.io) to sort load order automatically.

**Mod not showing content:** Confirm the plugin (.esp) is enabled in your mod manager's plugin tab.

**Conflicts with other mods:** Use your mod manager's conflict detection to identify overlapping assets. The mod with lower priority in the load order loses its assets where conflicts exist — adjust accordingly.

---
Sources:
- [Nexus Mods — IKEA Home Furnishings](https://www.nexusmods.com/skyrimspecialedition/mods/53704)
- [SKSE64 official](https://skse.silverlock.org/)
- [Mod Organizer 2](https://modorganizer2.github.io/)
- [LOOT](https://loot.github.io/)
- [Nexus Mods — Vortex installation guide](https://wiki.nexusmods.com/index.php/Installing_mods_with_Vortex)
