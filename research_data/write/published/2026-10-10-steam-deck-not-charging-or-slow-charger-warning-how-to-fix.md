---
layout: single
title: 'Steam Deck Not Charging or "Slow Charger" Warning: How to Fix It'
date: 2026-10-10 14:56:00 +0000
categories: [gaming]
tags: ["guide", "steam", "deck", "charging"]
excerpt: 'If your Steam Deck shows a "Slow Charger" warning or the battery percentage won''t go up, the cause is usually the charger, the cable, or a dock sharing…'
author_profile: false
read_time: true
share: true
---

If your Steam Deck shows a "Slow Charger" warning or the battery percentage won't go up, the cause is usually the charger, the cable, or a dock sharing power, not the battery itself. Work through the checks below in order. Most take under a minute.

*Checked October 8, 2026. Menu names vary by SteamOS version.*

---

## What charger the Steam Deck needs

Valve lists a 45W USB-C Power Delivery (PD) input for the Steam Deck, and the charger in the box is rated at 45W. According to [iFixit's Steam Deck charging guide](https://www.ifixit.com/Wiki/Steam_Deck_Not_Charging), a charger below what the Deck needs can trigger a "Slow Charge" warning, and a more powerful charger may be needed to run the system and refill the battery at the same time.

A higher number on the label doesn't guarantee a fix. A phone fast-charge mode is not the same as USB-C PD, and a weak or damaged cable can limit power even with a strong charger. That is why the first tests below swap one part at a time.

---

## Fix it in this order

1. **Restart the Deck.** Hold the power button and choose Restart. This clears many temporary charging glitches.
2. **Test the charger and cable.** iFixit suggests trying the Deck's charger on another USB-C device, or trying another charger on the Deck. Plug the supplied charger straight into the Deck, with no dock or multi-port charger in between, and see whether the warning goes away.
3. **Check the dock.** If the warning only appears on a dock, unplug the dock and connect the charger directly. Docks and multi-port chargers can share power with connected devices, so unplug storage, Ethernet, and other accessories and test again.
4. **Inspect the port.** Look into the USB-C port with a flashlight. Clear lint with a non-metal tool, and make sure the plug sits fully in the port.
5. **Update SteamOS.** iFixit lists checking for a SteamOS update as a step. Update from Game Mode.
6. **Try Battery Storage Mode.** If the earlier steps didn't help, iFixit suggests putting the Deck into Battery Storage Mode and then powering it on normally. You reach it from the Deck's Setup Utility (power off, then hold Volume Up and tap the power button), where the Power menu lists Battery Storage Mode. The exact menu names depend on the BIOS version.
7. **Check battery health.** In Desktop Mode, click the battery icon in the lower right corner. The battery's health percentage appears below the charge level, as iFixit describes. Signs of a swollen battery, such as a gap in the case, mean you should contact Valve.

---

## If the battery stops at 80% or doesn't reach 100%

- **A charge limit may be on.** SteamOS has a Battery Charge Limit setting, which Valve introduced in a SteamOS 3.7.7 beta in May 2025. An 80% limit can help long-term battery health if the Deck is docked a lot. If it stops at a steady 80%, check that setting before assuming the battery is faulty.
- **A Deck left plugged in can sit slightly below 100%.** That is normal behavior meant to protect the battery.
- **Gaming while charging wears the battery faster.** iFixit notes that playing while plugged in is expected but reduces battery longevity over time.

---

## When to contact Valve

If the supplied charger, connected directly, still fails after the steps above, stop swapping accessories and contact Steam Support. Don't open the Deck just to test chargers.

---

## Takeaway

Start with the supplied 45W charger plugged straight into the Deck. If the warning disappears, the dock, cable, or third-party charger was the problem. If it doesn't, work through restart, update, and Battery Storage Mode, and contact Valve if it still won't charge.

---
Sources:
- [iFixit — Steam Deck Not Charging](https://www.ifixit.com/Wiki/Steam_Deck_Not_Charging)
- [Valve — Steam Deck technical specifications](https://www.steamdeck.com/en/tech)
