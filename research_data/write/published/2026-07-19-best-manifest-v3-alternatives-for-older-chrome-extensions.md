---
layout: single
title: 'Best Manifest V3 Alternatives: uBlock Origin Lite and More (2026)'
date: 2026-07-19 10:00:00 +0900
last_modified_at: 2026-10-21 00:00:00 +0900
categories: [tech]
tags: ["chrome extensions", "manifest v3 alternatives", "ublock origin lite", "ad blocker replacement"]
excerpt: 'Chrome disabled the original uBlock Origin in July 2025. What uBlock Origin Lite, AdGuard and Adblock Plus can do under MV3, and where the full one still runs.'
header:
  image: https://images.frontbuffer.net/posts/best-manifest-v3-alternatives-for-older-chrome-extensions/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

If the original uBlock Origin stopped working in Chrome, the cause is the Manifest V2 shutdown, and the replacement options fall into two groups: MV3 extensions that work inside Chrome's limits, and browsers that still run the full version. [Chrome's timeline](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline) says Chrome 138 disabled MV2 extensions everywhere in July 2025, and all remaining MV2 extensions were removed from the Web Store on August 31, 2026.

*Checked October 16, 2026 against official pages and press reports. The Brave and Adblock Plus release details were re-checked on October 21, 2026. No independent blocking test was checked, so this page does not rank blockers by how much they block. Nothing here was tested in a browser.*

---

## Options inside Chrome

| Option | What to know |
|---|---|
| **uBlock Origin Lite** | The MV3 version of uBlock Origin. Its [official FAQ](https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-%28FAQ%29) says capabilities such as dynamic filtering cannot be supported under MV3 |
| **AdGuard** | Publishes an MV3 browser extension. [AdGuard's blog post](https://adguard.com/blog/adguard-mv3.html), written in 2022 when it released its first MV3 prototype, says the declarative rule syntax severely limits what an extension can do |
| **Adblock Plus** | [Adblock Plus 4.0](https://blog.adblockplus.org/releases/adblock-plus-40-for-chrome-firefox-microsoft-edge-and-opera), released April 29, 2024, was its first MV3-based version, for Chrome users at first. [Version 4.1](https://blog.adblockplus.org/releases/adblock-plus-41-for-chrome-firefox-microsoft-edge-and-opera), released May 28, 2024, reintroduced third-party filter lists for MV3. Its maker, eyeo, says the extensions allow ads that meet the [Acceptable Ads Standard](https://resources.eyeo.com/mv3-ready) |

The MV3 limit all three work under comes from how Chrome now handles network requests. Chrome's [own overview](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3) says it deprecated the blocking webRequest API, which required extensions to proxy network traffic, and calls declarativeNetRequest a safer alternative for many use cases. The ad-blocker makers above describe the same change as a restriction. Both statements are true to their sources, and which one matters depends on what you want your blocker to do.

The uBlock Origin Lite FAQ gives the specific reason dynamic filtering is out: declarativeNetRequest cannot apply rules according to the page you are on, and building it on webRequest instead would wake the extension's service worker constantly and defeat the point of the Lite version.

Two more limits show up in the makers' own notes. Adblock Plus said its first MV3 release had a significantly larger package size and temporarily disabled third-party filter lists. Those lists came back in version 4.1. And eyeo, which makes Adblock Plus, says Chrome enforces limits on rulesets and on static and dynamic rules in MV3. AdGuard's 2022 post gives the numbers at that time: a guaranteed minimum of 30,000 static rules per extension, 330,000 in total across a user's extensions, and 5,000 dynamic rules. Chrome may have changed these limits since, so treat them as a snapshot.

Chrome itself nudged people toward these options. Its timeline says that when it began disabling installed MV2 extensions in October 2024, it sent users to the Web Store, where they were shown recommended MV3 alternatives for the extension that was turned off.

---

## Which option fits

| If you want | Look at | Why, per the sources |
|---|---|---|
| The closest match to the old uBlock Origin, from the same project | uBlock Origin Lite | It is the MV3 version, with dynamic filtering unavailable |
| A blocker that allows ads meeting a standard | Adblock Plus | eyeo says it allows ads that meet the Acceptable Ads Standard |
| Another MV3-native blocker | AdGuard | It publishes an MV3 extension and explains the limits of Chrome's declarative rules |
| Full filtering control and per-site rules | Firefox with uBlock Origin | Mozilla keeps MV2 and the blocking webRequest API |

Whichever you choose, test it on the sites you actually use, since no independent comparison was checked here.

---

## Options outside Chrome

- **Firefox.** Mozilla says it keeps MV2 alongside MV3 and [continues to support the blocking webRequest API](https://blog.mozilla.org/en/products/firefox/firefox-manifest-v3-adblockers/). The full uBlock Origin runs there. For how to get the old uMatrix-style control back with it, see [What to Use Instead of uMatrix in 2026](https://frontbuffer.net/tech/what-to-use-instead-of-umatrix-in-2026/).
- **Brave.** Brave's own [Manifest V3 post](https://brave.com/blog/brave-shields-manifest-v3/) says it hosts four MV2 extensions on its own servers, AdGuard, uBlock Origin, uMatrix and NoScript, and will keep supporting them for as long as it is able and the extension authors cooperate. In August 2026 Brave also [wrote on X](https://x.com/brave/status/2087227867646079410) that it keeps supporting uBlock Origin, with the toggle under Settings, Extensions, Manifest v2 extensions.

---

## For developers

Chrome's overview says MV3 moves background code to service workers that run only when needed and removes remotely hosted code, so an extension can only run JavaScript included in its own package. The [migration overview](https://developer.chrome.com/docs/extensions/develop/migrate) and its checklist are the starting point.

There is a GoogleChromeLabs [Extension Manifest Converter](https://github.com/GoogleChromeLabs/extension-manifest-converter) on GitHub. Its repository says it converts using search-and-replace changes, does not fully automate the work, and is not an official Google product. The repository was archived on April 19, 2026 and is read-only.

---

If you are not sure whether an extension is MV2, see [How to Check If a Chrome Extension Uses Manifest V2](https://frontbuffer.net/tech/how-to-check-if-chrome-extensions-use-manifest-v2/). The full timeline is in the [Chrome Manifest V2 hub](https://frontbuffer.net/tech/google-chrome-manifest-v2-migration_HUB/).

---

Sources:

- [Manifest V2 support timeline, Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline)
- [What is Manifest V3, Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3)
- [Migrate to Manifest V3, Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/migrate)
- [Frequently asked questions, uBlock Origin Lite wiki](https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-%28FAQ%29)
- [AdGuard publishes the world's first ad blocker built on Manifest V3, AdGuard](https://adguard.com/blog/adguard-mv3.html)
- [Adblock Plus 4.0 for Chrome, Firefox, Microsoft Edge and Opera, Adblock Plus Blog](https://blog.adblockplus.org/releases/adblock-plus-40-for-chrome-firefox-microsoft-edge-and-opera)
- [Adblock Plus 4.1 for Chrome, Firefox, Microsoft Edge and Opera, Adblock Plus Blog](https://blog.adblockplus.org/releases/adblock-plus-41-for-chrome-firefox-microsoft-edge-and-opera)
- [MV3 ready, eyeo](https://resources.eyeo.com/mv3-ready)
- [Mozilla's approach to Manifest V3, Mozilla Blog](https://blog.mozilla.org/en/products/firefox/firefox-manifest-v3-adblockers/)
- [What Manifest V3 means for Brave Shields and the use of extensions in the Brave browser, Brave](https://brave.com/blog/brave-shields-manifest-v3/)
- [Brave on X: we host uBlock Origin and other Manifest v2 extensions, August 11, 2026, Brave](https://x.com/brave/status/2087227867646079410)
- [Extension Manifest Converter, GoogleChromeLabs on GitHub](https://github.com/GoogleChromeLabs/extension-manifest-converter)
