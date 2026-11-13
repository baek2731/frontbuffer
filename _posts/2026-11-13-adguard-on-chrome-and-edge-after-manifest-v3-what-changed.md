---
layout: single
title: 'AdGuard on Chrome and Edge After Manifest V3: What Changed'
date: 2026-11-13 14:10:00 +0000
categories: [tech]
tags: ["explainer", "adguard", "manifest-v3", "chrome-extensions"]
excerpt: 'AdGuard''s browser extension now runs on Manifest V3 in Chrome and Edge. What AdGuard says changes, how custom filters work in Edge, and which numbers are dated.'
author_profile: false
read_time: true
share: true
---

AdGuard's browser extension now runs on Manifest V3 (MV3) in Chrome, and AdGuard has added an MV3 version for Microsoft Edge. AdGuard says most existing Chrome users need to do nothing. What does change, by AdGuard's own account, is that the browser applies a prebuilt ruleset, the number of active rules is limited, some rules cannot be converted exactly, and most filter updates now arrive with the extension itself.

*Checked October 28, 2026 against AdGuard's blog and its browser extension release notes on GitHub. On November 12, 2026 we re-opened those pages, AdGuard's MV3 beta announcement, the uBOL FAQ, and Microsoft's Edge blog post and developer timeline, and checked the claims below against them.*

## Chrome

In a post about Chrome removing its Manifest V2 extension from the Web Store, [AdGuard says](https://adguard.com/en/blog/adguard-adblocker-manifestv2-removal.html) it rebuilt AdGuard Ad Blocker for MV3 and that the MV3 version became its primary Chrome extension in September 2024. It describes tools it built to convert traditional filters into MV3 rules, and an engine of its own that it kept for hiding ads and other elements on pages. It also says it found ways to deliver urgent fixes within MV3's allowance for dynamic rules, and that custom filters in MV3 can again update independently of the extension. The same post names one group that does need to act: people who installed the separately listed AdGuard Ad Blocker MV2 extension must install the current AdGuard Ad Blocker manually, because Chrome treats the MV2 listing as a different extension and cannot replace it automatically.

## Edge

AdGuard's [5.5.3.3 release notes](https://github.com/AdguardTeam/AdguardBrowserExtension/releases/tag/v5.5.3.3), published September 30, say AdGuard's MV3 extension was added to Microsoft Edge, and that MV2 ad blockers no longer appear in Edge Add-ons search results. The notes tie this to Microsoft's policy on moving away from MV2 extensions, announced in August, and say AdGuard is not leaving the store.

To use custom filters and user rules in Edge, the same notes say to turn on **Allow user scripts** for the AdGuard Browser Extension: open `edge://extensions` (or choose Extensions, then Manage extensions), find AdGuard, click **Details** and switch it on.

Microsoft's [August 7 post on the Edge blog](https://blogs.windows.com/msedgedev/2026/08/07/moving-the-microsoft-edge-extensions-ecosystem-forward-with-manifest-version-3/) says Edge began its consumer move away from MV2 in August 2026, starting in the Canary, Dev and Beta channels and widening to Stable in the following months, with a goal of finishing by the end of 2026. MV2 extensions are to be turned off by default gradually, after notices and with pointers to MV3 versions where they exist. Managed devices are left out of the consumer rollout, and enterprise deprecation follows in early 2027. Microsoft's [developer timeline](https://learn.microsoft.com/microsoft-edge/extensions/developer-guide/manifest-v3), last updated September 15, 2026, lists warnings for some users from mid-September 2026 and gives no date for turning MV2 off in Stable. We did not find a Microsoft notice that Stable has already switched MV2 extensions off.

## What MV3 changes in practice

AdGuard's release notes put it this way. With MV2 the extension sees each network request in real time and decides what to block. With MV3 the browser receives a prebuilt ruleset and applies it. That means:

- the number of active rules is limited
- some traditional filtering rules cannot be converted exactly
- most filter updates ship with the extension, so they can take longer

AdGuard adds that everyday filtering stays close to MV2 for most people, but the browser now makes more of the decisions and keeping behavior close to MV2 takes more work.

The underlying limits are the ones that apply to every MV3 blocker. The uBOL project's FAQ gives a guaranteed 30,000 static rules and a global limit of 330,000 in Chromium. AdGuard's MV3 beta announcement from July 2024 describes the 330,000 as shared across all of a user's extensions and lists further limits, including a maximum of 50 filters enabled at once. That post is more than two years old and predates the changes above, so treat its numbers as dated and check the current extension.

## If you want to avoid the extension limits

AdGuard's own suggestion is a system-wide AdGuard app for Windows, Mac, Android or Linux, which it says filters traffic across browsers and other applications and does not depend on a browser's extension rules. We did not check whether such an app is free or paid.

## How it differs from uBlock Origin Lite

Both are MV3 blockers. AdGuard says it kept an engine of its own for hiding page elements, while the uBOL project describes Lite as entirely declarative. We found no independent test comparing how well they block, so we do not rank them. Our guide to [uBlock Origin Lite's modes and limits](https://frontbuffer.net/tech/ublock-origin-lite-filtering-modes-settings-and-limits/) covers the other side.

## What we could not confirm

- AdGuard's current rule and filter limits on Chrome and Edge, since its older numbers are dated.
- How closely the MV3 build matches the old MV2 extension on difficult sites. AdGuard's statements are its own.
- When Edge will turn MV2 extensions off for everyone on Stable. Microsoft gives an end-of-2026 goal, not a date.
- Whether people who already have AdGuard in Edge are moved to the MV3 build automatically. The release notes also list an MV2 build for Edge.
- Whether Allow user scripts is needed in browsers other than Edge.

---
Sources:
- [The Manifest V2 era is over: Chrome removes AdGuard Ad Blocker MV2 from the Web Store, AdGuard](https://adguard.com/en/blog/adguard-adblocker-manifestv2-removal.html)
- [AdGuard Browser Extension v5.5.3.3 release notes, GitHub](https://github.com/AdguardTeam/AdguardBrowserExtension/releases/tag/v5.5.3.3)
- [Moving the Microsoft Edge extensions ecosystem forward with Manifest Version 3, Microsoft Edge Blog](https://blogs.windows.com/msedgedev/2026/08/07/moving-the-microsoft-edge-extensions-ecosystem-forward-with-manifest-version-3/)
- [Timeline for migrating to Manifest V3, Microsoft Edge Developer documentation](https://learn.microsoft.com/microsoft-edge/extensions/developer-guide/manifest-v3)
- [Manifesting change: AdGuard Ad Blocker on MV3 moves from prototype to beta, AdGuard](https://adguard.com/en/blog/adguard-mv3-beta.html)
- [Frequently asked questions (FAQ), uBOL-home Wiki](https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-%28FAQ%29)

