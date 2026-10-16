---
layout: single
title: "Chrome Manifest V2 Is Dead: What Happened and What to Use Instead"
date: 2026-07-20 11:11:27 +0900
last_modified_at: 2026-10-16 00:00:00 +0900
categories: [tech]
tags: ["hub", "chrome", "manifest-v2", "manifest-v3"]
excerpt: 'Chrome removed all Manifest V2 extensions from the Web Store on August 31, 2026. Check what still works, and find MV3 replacements for uBlock Origin.'
header:
  image: https://images.frontbuffer.net/posts/google-chrome-manifest-v2-migration_HUB/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

If an extension you relied on, uBlock Origin being the best-known, stopped working in Chrome, or the Chrome Web Store says it is unavailable, this is why. [Chrome's official timeline](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline) says all remaining Manifest V2 (MV2) extensions were removed from the Web Store on August 31, 2026. This page explains what that means for extensions you already have, and points you to the right guide.

*Checked October 16, 2026 against Chrome's timeline page, which was last updated on September 9, 2026.*

---

## Short answer

- **You cannot install MV2 extensions from the Web Store anymore.** Chrome says all remaining ones were removed on August 31, 2026.
- **Installs on Chrome 138 or earlier keep running,** but they can no longer receive updates and cannot be reinstalled if removed, according to Chrome.
- **Chrome 139 and newer do not run MV2 extensions.** Chrome says MV2 extensions cease to function for anyone upgrading to Chrome 139 and later, and Android Authority adds that Chrome 139 and newer support only Manifest V3 (MV3).
- **Firefox still supports MV2.** Mozilla says it keeps Manifest V2 alongside Manifest V3 and [continues to support the blocking webRequest API](https://blog.mozilla.org/en/products/firefox/firefox-manifest-v3-adblockers/). Other Chromium-based browsers differ. [BetaNews reports](https://betanews.com/article/firefox-brave-ublock-origin-chrome-edge/) that Brave said it hosts uBlock Origin and other MV2 extensions on its own servers, and that Edge is phasing MV2 out.

---

## How we got here

| When | What changed |
|---|---|
| January 2022 | The Web Store stopped accepting new public and unlisted MV2 extensions |
| June 2022 | It also stopped accepting new private MV2 extensions |
| June 2024 | The phase-out began, with a warning banner on `chrome://extensions` in Chrome's pre-stable channels |
| October 2024 | Chrome began disabling installed MV2 extensions in the stable channel |
| March 31, 2025 | MV2 extensions were disabled by default for all users, who could still turn them back on |
| July 24, 2025 (Chrome 138) | MV2 extensions disabled everywhere. Chrome says users can no longer turn them back on |
| Chrome 139 | The enterprise policy for MV2 was removed, and MV2 extensions stopped working on upgrade |
| June 2026 | Android Authority reports Chrome removed the flag that let users bypass the restrictions |
| August 31, 2026 | All remaining MV2 extensions were removed from the Web Store |

Everything except the June 2026 row comes from Chrome's timeline. Chrome's page says users could no longer re-enable MV2 extensions from July 2025, while [Android Authority says](https://www.androidauthority.com/google-chrome-old-manifest-v2-extensions-delete-3685207/) it stayed almost impossible until the flag was removed in June 2026. The two sources differ on that point.

---

## Where to start

**Your extension disappeared or stopped working, and you want to know why.**
Google's Manifest V3 changed how extensions run in the browser. It is a stricter platform with limits on background processes, data access and remotely hosted code, and those limits are why tools like the original uBlock Origin no longer work in Chrome.

→ Read more: [What is Chrome Manifest V3 and Why Extensions Break](https://frontbuffer.net/tech/what-is-chrome-manifest-v3-and-why-extensions-break/)

**You want to know which of your extensions are still on MV2.**
On Chrome 139 and newer, MV2 extensions do not run, so the question matters mostly for Chrome 138 or earlier and for other browsers. The guide covers how to check an extension's manifest version.

→ Read more: [How to Check If Chrome Extensions Use Manifest V2](https://frontbuffer.net/tech/how-to-check-if-chrome-extensions-use-manifest-v2/)

**You need a replacement that works under the new rules.**
uBlock Origin Lite is the MV3 version of uBlock Origin, and its [official FAQ](https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-%28FAQ%29) says features such as dynamic filtering cannot be supported under MV3. AdGuard also publishes an MV3 extension, and [its blog explains](https://adguard.com/blog/adguard-mv3.html) that Chrome's declarative rules severely limit what an ad blocker can do. Firefox keeps the full uBlock Origin.

→ Read more: [Best Manifest V3 Alternatives for Older Chrome Extensions](https://frontbuffer.net/tech/best-manifest-v3-alternatives-for-older-chrome-extensions/)

---

## Takeaway

If an MV2 extension still runs because you are on Chrome 138 or earlier, treat it as temporary. It will not update, it cannot be reinstalled from the Web Store, and a new computer or clean install will not bring it back. Check what you have, choose an MV3 replacement or a browser that still supports MV2, and test it before you change anything.

---
## Sources

- [Manifest V2 support timeline, Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline)
- [Google is about to delete some of your favorite Chrome extensions forever, Android Authority](https://www.androidauthority.com/google-chrome-old-manifest-v2-extensions-delete-3685207/)
- [Mozilla's approach to Manifest V3, Mozilla Blog](https://blog.mozilla.org/en/products/firefox/firefox-manifest-v3-adblockers/)
- [Firefox and Brave keep uBlock Origin as Chrome and Edge phase out support, BetaNews](https://betanews.com/article/firefox-brave-ublock-origin-chrome-edge/)
- [Frequently asked questions, uBlock Origin Lite wiki](https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-%28FAQ%29)
- [AdGuard publishes the world's first ad blocker built on Manifest V3, AdGuard](https://adguard.com/blog/adguard-mv3.html)
