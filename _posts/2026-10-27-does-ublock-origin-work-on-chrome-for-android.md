---
layout: single
title: 'Does uBlock Origin Work on Chrome for Android?'
date: 2026-10-27 14:29:00 +0000
categories: [tech]
tags: ["explainer", "ublock", "origin", "chrome", "android"]
excerpt: 'uBlock Origin doesn''t work on Chrome for Android. Find out why Chrome for Android lacks extension support and how Firefox for Android offers a solution.'
header:
  image: https://images.frontbuffer.net/posts/does-ublock-origin-work-on-chrome-for-android/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

No. Chrome for Android does not support extensions, so neither the full uBlock Origin nor uBlock Origin Lite can be installed in it. Firefox for Android can run the full uBlock Origin: Mozilla's add-on listing shows it as Recommended and available on Firefox for Android.

*Checked October 22, 2026 against Mozilla's add-on listing and 2026 reports. We did not find a Google statement on this, so the Chrome claim rests on the reports listed below. Nothing here was tested on a phone.*

## What the sources say about Chrome for Android

MakeUseOf wrote in 2026 that Chrome on Android has never supported extensions, not when it launched and not now. A Web Highlights guide says there is no setting or flag that turns them on. An Extension Booster guide says the Chrome app still had no extension support as of mid-2026. Installing uBlock Origin Lite in desktop Chrome does not add it to your phone, because Chrome for Android does not run desktop extensions.

## What works instead

- **Firefox for Android.** The [uBlock Origin listing on Mozilla's add-on site](https://addons.mozilla.org/en-US/addon/ublock-origin/) offers a QR code to open the extension in Firefox for Android. The steps are to install Firefox, open that page from the browser and add the extension.
- **Other browsers.** Web Highlights lists Vivaldi (8.2 and later, since September 2026) and a few smaller Chromium-based browsers as supporting extensions on Android. Reports disagree on Microsoft Edge for Android. Web Highlights says Edge installs extensions from its menu, while Extension Booster says only Edge Canary on Android has experimental extension support. Check Edge's own settings before relying on it.
- **Brave.** [PiunikaWeb reported on October 1, 2026](https://piunikaweb.com/2026/10/01/brave-starts-work-android-extensions/) that Brave developers have started building Android extension support, covering both Manifest V3 and Manifest V2 extensions. That report describes work in progress, not a released feature.

## Blocking outside the browser

One site, Adblock Tester, suggests a system-level app or DNS-based blocking that covers every app, because Chrome for Android cannot run extensions. We did not evaluate such tools, so treat that as one site's suggestion.

## What this means for you

If you want uBlock Origin on a phone, the verified route is Firefox for Android. If you stay on Chrome for Android, an extension is not an option, and desktop settings will not follow you to your phone.

## What we could not confirm

- Whether Google plans extension support for Chrome on Android. We found no announcement.
- Edge for Android's current extension status, since the reports conflict.
- When, or whether, Brave's Android extension support will ship.

For the desktop side of the story, see our guide to [what to use as Manifest V2 extensions disappear from Chrome](https://frontbuffer.net/tech/best-manifest-v3-alternatives-for-older-chrome-extensions/).

---
Sources:
- [uBlock Origin by Raymond Hill, Firefox Browser Add-ons](https://addons.mozilla.org/en-US/addon/ublock-origin/)
- [Chrome can't use Android extensions, but these 5 mobile browsers can, MakeUseOf](https://www.makeuseof.com/android-browsers-that-run-extensions-chrome-keeps-leaving-out/)
- [Chrome Extensions on Android: How to Install Them in 2026, Web Highlights](https://web-highlights.com/blog/how-to-install-chrome-extensions-on-android/)
- [Chrome Extensions on Android in 2026: What Actually Works, Extension Booster](https://extensionbooster.net/blog/chrome-extensions-android-2026-what-works-guide/)
- [Brave browser officially starts work on Android extension support, PiunikaWeb](https://piunikaweb.com/2026/10/01/brave-starts-work-android-extensions/)
- [How to Fix uBlock Origin Not Working on Chrome (2026), Adblock Tester](https://adblock-tester.com/ad-blockers/how-to-fix-ublock-origin-chrome/)
