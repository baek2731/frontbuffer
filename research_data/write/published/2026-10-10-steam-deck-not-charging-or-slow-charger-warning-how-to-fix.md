---
layout: single
title: 'Steam Deck Not Charging or "Slow Charger" Warning: How to Fix It'
date: 2026-10-10 14:56:00 +0000
last_modified_at: 2026-10-16 00:00:00 +0000
categories: [gaming]
tags: ["guide", "steam", "deck", "charging"]
excerpt: 'A Slow Charger warning or a Deck that won''t charge often starts with the power source. A check order based on iFixit''s guide, plus the Battery Charge Limit.'
header:
  image: https://images.frontbuffer.net/posts/steam-deck-not-charging-or-slow-charger-warning-how-to-fix/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

If your Steam Deck shows a "Slow Charger" warning or the battery percentage will not climb, start with the power source. iFixit's troubleshooting guide lists a weak power source first among the causes, followed by software, the battery, the charge port and the motherboard. This guide follows that order and keeps general advice separate from what iFixit says.

*Checked October 16, 2026. Menu names vary by SteamOS version, and nothing here was tested on a Deck.*

---

## What charger the Deck needs

[iFixit says](https://www.ifixit.com/Wiki/Steam_Deck_Not_Charging) a Steam Deck idles at about 15 watts, so a charger has to exceed that to raise the battery level, and the charger in the box is 45 watts. Anything below that may produce a "Slow Charge" warning, and a more powerful charger may be needed to run the system and refill the battery at the same time. [Android Authority](https://www.androidauthority.com/steam-deck-charger-wattage-3339790/) says Valve's bundled USB-C charger supplies 45W, that you do not need a charger made for the Deck, and that the cable should at least be marked as USB Power Delivery. A phone fast-charge mode is a different standard from USB-C PD.

---

## Fix it in this order

1. **Restart the Deck.** iFixit lists this as the first basic step.
2. **Check the charger and outlet.** Look at the LED near the charge port. iFixit suggests using the Deck's charger on another USB-C device, or another charger on the Deck, and trying a wall outlet you know works.
3. **Try the other mode.** iFixit says to switch between Desktop Mode and Game Mode depending on where the problem happens. If it charges in the other mode, a software fault is the likely cause.
4. **Plug the charger straight in.** This is general advice, not from iFixit: connect the supplied charger and cable directly to the Deck with no dock, hub or multi-port charger in between, so you know whether an accessory is the problem.
5. **Inspect the port.** iFixit says to look into the USB-C port with a flashlight and, if it is clogged, use an air duster and a toothpick shaved to fit. It warns against inserting anything metal.
6. **Update SteamOS.** iFixit says updates are installed in Game Mode and may include a fix. If no update is available, it points to Valve's guidance for reinstalling or reimaging the system.
7. **Try Battery Storage Mode.** iFixit says putting the Deck into Battery Storage Mode and then powering it on normally resets the charging circuitry and may clear errors. See the cautions below before you use it.
8. **Check battery health.** In Desktop Mode, click the battery icon in the lower right corner. iFixit says the battery's health percentage appears below the charge level. It lists separation of the enclosure, localized screen discoloration and bowing of the housing as signs of a swollen battery. If you see those, contact Valve.

---

## Battery Storage Mode: cautions

[iFixit's guide](https://www.ifixit.com/Guide/How+to+Enable+Steam+Deck+Battery+Storage+Mode/149962) says Valve recommends this mode before repairs, and that it is also used for long-term storage. The steps it gives are:

1. Power down the Deck.
2. Hold **volume up** and press the **power** button, then release both to boot into the BIOS.
3. Use the D-pad to move and the A button to select. Go to **Setup Utility**, then **Power**, then **Battery storage mode**, and confirm with **Yes**.

In storage mode the Deck does not respond to the power button. To exit, plug it into the charger. For long-term storage, iFixit says to bring the battery to 50 to 60% first.

---

## If the battery stops at 80%

SteamOS has a **Battery Charge Limit** control under Settings, then Power. [GamingOnLinux reports](https://www.gamingonlinux.com/2025/05/steam-deck-gets-a-battery-charge-limit-control-in-the-latest-beta/) that Valve added it in a Steam Deck beta client release on May 8, 2025, and its release notes say a limit of 80% can help long-term battery health for a Deck that is constantly charged, such as one that is docked. The control later appeared in a [SteamOS 3.7.7 beta](https://www.gamingonlinux.com/2025/05/steamos-3-7-7-beta-brings-a-battery-charge-limit-option-and-improved-lenovo-legion-go-s-support/).

If the Deck stops at a steady 80%, check that setting before assuming the battery is faulty. Two user reports on Valve's SteamOS issue tracker are worth knowing. One says the [charge LED stays white at the limit instead of turning green](https://github.com/ValveSoftware/SteamOS/issues/2018). Another says the [Deck sometimes charges past the limit](https://github.com/ValveSoftware/SteamOS/issues/2674). Those are user reports, not confirmed by Valve.

iFixit also notes that playing while plugged in is an expected part of using the Deck but reduces battery longevity over time.

---

## When to contact Valve

If the supplied charger, plugged straight into the Deck, still fails after these steps, contact Steam Support. iFixit says board faults in the first year without accidental damage are rare and should be covered by warranty.

---
Sources:
- [Steam Deck Not Charging, iFixit](https://www.ifixit.com/Wiki/Steam_Deck_Not_Charging)
- [How to Enable Steam Deck Battery Storage Mode, iFixit](https://www.ifixit.com/Guide/How+to+Enable+Steam+Deck+Battery+Storage+Mode/149962)
- [What wattage is the official Steam Deck charger, Android Authority](https://www.androidauthority.com/steam-deck-charger-wattage-3339790/)
- [Steam Deck gets a Battery Charge Limit control in the latest Beta, GamingOnLinux](https://www.gamingonlinux.com/2025/05/steam-deck-gets-a-battery-charge-limit-control-in-the-latest-beta/)
- [SteamOS 3.7.7 Beta brings a Battery Charge Limit option, GamingOnLinux](https://www.gamingonlinux.com/2025/05/steamos-3-7-7-beta-brings-a-battery-charge-limit-option-and-improved-lenovo-legion-go-s-support/)
- [Charge LED does not reflect the charge limit, ValveSoftware/SteamOS issue 2018, GitHub](https://github.com/ValveSoftware/SteamOS/issues/2018)
- [Battery Charge Limit does not always work correctly, ValveSoftware/SteamOS issue 2674, GitHub](https://github.com/ValveSoftware/SteamOS/issues/2674)
