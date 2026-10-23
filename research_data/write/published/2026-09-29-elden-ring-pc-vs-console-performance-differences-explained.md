---
layout: single
title: 'Elden Ring PC vs console performance: what actually differs'
date: 2026-09-29 14:56:00 +0000
last_modified_at: 2026-10-20 00:00:00 +0000
categories: [gaming]
tags: ["comparison", "elden-ring", "pc", "performance"]
excerpt: 'Elden Ring launched with PC stutter and variable console frame rates. What launch-era analysis found, what fixes helped on PC, and the anti-cheat rule for mods.'
header:
  image: https://images.frontbuffer.net/posts/elden-ring-pc-vs-console-performance-differences-explained/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

If Elden Ring stutters on your PC, a faster graphics card may not fix it. Digital Foundry's launch analysis found PC problems that affected all hardware and all presets, while the PS5 and Xbox Series versions had variable frame rates of their own. This post compares the two and lists fixes that were reported to help on PC.

*Checked October 20, 2026. Most of our sources date from February and March 2022, so they describe launch-era builds. We have not benchmarked current builds, and patches since may have changed things. Check the current patch notes on Steam.*

---

## Short answer

- **Console:** the simpler choice, with no settings to manage, though frame rates were variable at launch.
- **PC:** the better choice if you want mods or already own capable hardware, with the expectation of some stutter and tinkering.

---

## PC at launch

[Windows Central quoted Digital Foundry](https://windowscentral.com/elden-ring-faces-mixed-pc-reviews-over-widespread-performance-issues) saying the 1.02 PC build had issues that affect all hardware configurations on all graphical presets, and that Elden Ring was FromSoftware's first foray into low-level APIs on PC, using DirectX 12. [Digital Foundry's first impressions](https://www.eurogamer.net/articles/digitalfoundry-2022-02-24-elden-ring-performance-first-impressions) describe a stutter tied to loading new areas: minor one-off frame drops a few times a minute, or at worst frame-time problems that dropped the rate from a steady 60 into the 40s.

Bandai Namco said its day-one patch, 1.02, would improve stability, and later told players that updating graphics drivers may significantly improve performance. [PC Gamer reported](https://www.pcgamer.com/elden-ring-stuttering-day-one-patch/) that the day-one patch fixed the worst stuttering but that some persisted in new areas.

---

## Consoles at launch

Digital Foundry found that on patch 1.02, the frame-rate mode ran at 45 to 60 fps on PS5 and Series X, while the quality modes ranged between 30 and 60 fps. So console problems were about inconsistency within a fixed target, while the PC stutter came from frame pacing.

---

## What patches changed

[Digital Trends found](https://www.digitaltrends.com/computing/elden-ring-new-patch-stuttering-how-to-fix/) that patch 1.02.2 still stuttered on its test system. We did not verify later patches, so treat any claim that the PC version is fully fixed with caution.

---

## What to try on PC

1. **Update your graphics driver.** This was Bandai Namco's first recommendation.
2. **Cap the frame rate just under 60.** Digital Trends found that setting a 59 fps cap in the driver made the biggest difference on its test system, an RTX 3090 and Core i9-10900K.
3. **Adjust the shader cache.** For NVIDIA, Digital Trends set Shader Cache Size to Unlimited and Power Management Mode to Prefer Maximum Performance. For AMD, it set Frame Rate Target Control to 59 fps and reset the shader cache.

These are launch-era fixes from one reviewer's PC, so results will differ.

---

## Mods and anti-cheat

Elden Ring uses Easy Anti-Cheat. [Den of Geek warns](https://www.denofgeek.com/games/elden-ring-best-mods-download-pc/) that it may react to even benign mods, so disable it before modding and use mods only offline. [Windows Central's guide](https://windowscentral.com/how-disable-anti-cheat-elden-ring) says disabling it starts the game in offline mode, and that going back online with modified save files could lead to a temporary ban from online play. Do not run mods while connected to online play.

---

## Which one to pick

**Pick console** if you want to launch and play, or you play online with friends and do not want to think about anti-cheat.

**Pick PC** if you already own capable hardware, want mods for offline runs, and can live with some stutter. Check driver and patch notes after major updates.

---

Sources:
- [Elden Ring team acknowledges PC issues, new patch coming soon, Windows Central](https://windowscentral.com/elden-ring-faces-mixed-pc-reviews-over-widespread-performance-issues)
- [Elden Ring performance first impressions, Digital Foundry](https://www.eurogamer.net/articles/digitalfoundry-2022-02-24-elden-ring-performance-first-impressions)
- [Elden Ring's day-one patch fixed the worst stuttering issues but some persist, PC Gamer](https://www.pcgamer.com/elden-ring-stuttering-day-one-patch/)
- [Elden Ring's new patch still stutters, Digital Trends](https://www.digitaltrends.com/computing/elden-ring-new-patch-stuttering-how-to-fix/)
- [Elden Ring: Best Mods You Need to Download, Den of Geek](https://www.denofgeek.com/games/elden-ring-best-mods-download-pc/)
- [How to disable Easy Anti-Cheat in Elden Ring and play offline, Windows Central](https://windowscentral.com/how-disable-anti-cheat-elden-ring)
