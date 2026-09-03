---
layout: single
title: 'How to Customize Pixel Quick Settings with Android 17 QPR2 Beta Features'
date: 2026-09-01 14:34:00 +0000
categories: [tech]
tags: ["guide", "pixel", "pro"]
excerpt: 'Android 17 QPR2 Beta 3 (August 14, 2026) added a redesigned Quick Settings editor, native App Lock, and lock-screen blur to Pixel devices. Stable release is scheduled for December 2026.'
header:
  image: https://images.frontbuffer.net/posts/how-to-customize-pixel-quick-settings-with-android-17-qpr2-f/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

Android 17 QPR2 Beta 3, released August 14, 2026, brought the biggest changes of the QPR2 cycle so far: a redesigned Quick Settings editor, native App Lock, expanded Dynamic Color, and lock-screen blur. Beta 4 followed on August 28 and reached Platform Stability. Stable release is scheduled for December 2026 alongside the December Pixel Feature Drop.

If you're on the Android Beta Program, these features are available now on Pixel 6a through Pixel 10 series (excluding Pixel 6 and 6 Pro, which have reached end of life).

---

## What Changed in Quick Settings

The Quick Settings editor redesign in QPR2 Beta 3 makes tile management more direct. Previously, editing required entering a separate mode with unclear affordances. The new editor shows available tiles in a bottom sheet that stays visible while you rearrange the active grid — you can see both your current layout and available tiles at the same time.

**Tile persistence.** Tiles now remember their position across reboots more reliably. Earlier Android 17 builds had an issue where custom tile arrangements would occasionally reset after a device restart.

**Quick Settings font scaling.** Tile labels now scale with your system font size setting, which matters for accessibility. Previously, Quick Settings labels were fixed regardless of font size preference.

---

## How to Customize Quick Settings on QPR2 Beta

The process is the same as standard Android, but the editor interface is different:

1. Swipe down twice to expand the full Quick Settings panel.
2. Tap the **pencil icon** (Edit) in the bottom-left corner.
3. The new bottom sheet appears showing inactive tiles. Drag tiles between the active grid and the sheet.
4. Tiles in the first row appear without expanding the panel — put your most-used toggles there.
5. Tap **Done** when finished.

---

## New App Lock (QPR2 Beta 3)

QPR2 Beta 3 added native App Lock to Android 17 — the first time Android has included this at the system level without requiring a third-party app or Samsung's implementation.

**How to enable:**

1. Go to **Settings → Privacy → App Lock**.
2. Authenticate with your fingerprint or PIN.
3. Toggle on any app you want locked.

Locked apps require biometric authentication each time they're opened. The lock persists across sessions — closing and reopening the app triggers the authentication prompt again.

**Supported devices:** Pixel 6a and later running QPR2 Beta 3 or later.

---

## Lock Screen Blur (QPR2 Beta 3)

A new blur effect option for the lock screen wallpaper was added in Beta 3.

**How to enable:**

1. Go to **Settings → Wallpaper & style**.
2. Scroll to **Lock screen** → **Blur intensity**.
3. Adjust the slider from 0 (no blur) to maximum.

The blur applies to the wallpaper behind your lock screen clock and notifications. It doesn't affect the always-on display.

---

## Status Bar Customization (QPR2 Beta 4)

Beta 4 (August 28) added status bar customization — the ability to show or hide specific status bar indicators and rearrange their order.

**How to enable:**

1. Go to **Settings → Display → Status bar**.
2. Toggle indicators on or off, or drag to reorder.

Available indicators vary by device. Pixel 9 and 10 series have the most options.

---

## Should You Install the Beta?

Beta 4 has reached Platform Stability, which means the API surface is finalized and major bugs are resolved. Day-to-day use is generally reliable. That said, some users have reported UI glitches and performance issues — banking apps and work tools that require a certified build may not function correctly on beta firmware.

If you need these features now, join the [Android Beta Program](https://www.google.com/android/beta). If stability is the priority, wait for the December 2026 stable release.

---
Sources:
- [9to5Google — Android 17 QPR2 Beta 3 features](https://9to5google.com/2026/08/14/android-17-qpr2-beta-3/)
- [Droid-Life — Android 17 QPR2 Beta 4](https://www.droid-life.com/2026/08/28/google-releases-android-17-qpr2-beta-4-for-pixel/)
- [TechPP — Android 17 QPR2 feature tracker](https://techpp.com/roundup/android-17/)
- [Android Beta Program](https://www.google.com/android/beta)
