---
layout: single
title: 'How to install IKEA-themed mods for Skyrim Anniversary Edition'
date: 2026-09-29 14:42:00 +0000
categories: [gaming]
tags: ["guide", "skyrim", "mods", "anniversary-edition"]
excerpt: 'Installing IKEA-style furniture mods on Skyrim Anniversary Edition takes a mod manager, a version check, and a few dependencies. Here is the step-by-step setup.'
header:
  image: https://images.frontbuffer.net/posts/how-to-install-ikea-themed-mods-for-skyrim-anniversary-editi/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

IKEA-style furniture mods add Scandinavian flat-pack furniture to Skyrim's houses. Most are simple plugin files, but on Anniversary Edition (AE) the game version can break anything that depends on SKSE. This guide covers the setup that avoids crashes, using Mod Organizer 2 or Vortex.

To find the mods themselves, search for "IKEA" on [Nexus Mods for Skyrim Special Edition](https://www.nexusmods.com/skyrimspecialedition), which hosts AE mods too. Pick one that lists support for your game version on its page.

---

## Why AE needs a version check

Skyrim Anniversary Edition runs on executable version 1.6.x. Many older mods were built for Special Edition 1.5.97. Plain plugin files (.esp) usually work on both, but mods that use SKSE64 or compiled plugins must match your executable version. Check the mod's Requirements section and recent comments before installing.

---

## Step 1: Back up your game

Copy the Skyrim Special Edition folder (Steam → steamapps → common → Skyrim Special Edition) to a safe location. If an install goes wrong, you can restore this copy.

---

## Step 2: Install a mod manager

Use [Mod Organizer 2](https://modorganizer2.github.io/) or [Vortex](https://www.nexusmods.com/about/vortex/). Both keep your game's Data folder clean and make removing or reordering mods easy. Dropping files straight into the Data folder is harder to undo and not recommended once you have more than a couple of mods.

---

## Step 3: Install SKSE64 and Address Library, only if the mod needs them

Open the IKEA mod's Requirements section on Nexus.

- If it lists **SKSE64**, download the build that matches your AE executable from [skse.silverlock.org](https://skse.silverlock.org/). A version mismatch causes crashes on launch.
- If it lists **Address Library for SKSE Plugins**, install the version for your game build as well. Most SKSE-based plugins on AE depend on it.
- If it lists neither, skip this step. Many furniture mods are plain plugins.

Tip: SKSE is easy to break when Steam updates Skyrim in the background. In Steam, open Skyrim's Properties → Updates and set it to update only when you launch the game.

---

## Step 4: Install the mod

1. Download the mod file from its Nexus page.
2. In your mod manager, choose "Install from file" and select the archive.
3. Enable the mod and let the manager deploy it.
4. Read the mod's description for load order notes. Some furniture mods must load after specific master files.

---

## Step 5: Find the furniture in game

Furniture mods add items in different ways: a crafting workbench, a chest placed in a specific house, or items you spawn with the console. The mod's Nexus page explains which one it uses.

To spawn items with the console:

1. Press the tilde key (~) to open the console.
2. Type `help "IKEA"` and press Enter to list matching items with their IDs.
3. Type `player.additem [item ID] 1`, using the full ID from the list. The first two digits depend on your load order, so copy the ID exactly as shown.

---

## Troubleshooting

**Crash on load:** Check that your SKSE64 build matches your AE executable and that Address Library is installed if required. Run [LOOT](https://loot.github.io/) to sort the load order.

**No IKEA items appear:** Confirm the plugin (.esp) is ticked in your manager's plugin list.

**Conflicts with other mods:** Use your manager's conflict view. Later plugins in the plugin list override earlier ones. In Mod Organizer 2's left pane, the mod with the higher priority number wins file conflicts.

---

## Takeaway

Check the Requirements section first. If the mod needs no SKSE, installation is a plain manager install and you should be done in a few minutes. If it does need SKSE, match the version to your game build and turn off automatic Steam updates for Skyrim so it stays that way.

---
Sources:
- [Nexus Mods — Skyrim Special Edition](https://www.nexusmods.com/skyrimspecialedition)
- [SKSE64 official](https://skse.silverlock.org/)
- [Mod Organizer 2](https://modorganizer2.github.io/)
- [Vortex mod manager](https://www.nexusmods.com/about/vortex/)
- [LOOT](https://loot.github.io/)
