---
layout: single
title: "Chrome Manifest V2 Is Dead: What Happened and What to Use Instead"
date: 2026-07-20 11:11:27 +0900
categories: [tech]
tags: ["hub", "chrome", "manifest-v2", "manifest-v3"]
excerpt: "Chrome removed all Manifest V2 extensions from the Web Store on August 31, 2026. Check what still works, and find MV3 replacements for uBlock Origin and more."
header:
  image: https://images.frontbuffer.net/posts/google-chrome-manifest-v2-migration_HUB/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

If an extension you relied on, uBlock Origin being the best-known, stopped working in Chrome, or the Chrome Web Store says it is unavailable, this is why. Chrome removed all remaining Manifest V2 (MV2) extensions from the Web Store on August 31, 2026. This page explains what that means for extensions you already have, and points you to the right guide.

*Updated October 6, 2026.*

---

## Short answer

- **You can't install MV2 extensions from the Web Store anymore.** Google removed all remaining ones on August 31, 2026.
- **Already-installed MV2 extensions** only stay installed on Chrome 138 or earlier, and they get no updates and can't be reinstalled from the Web Store. Chrome 139 and newer support only Manifest V3 (MV3) extensions.
- **Firefox still supports MV2.** Policy on other Chromium-based browsers differs and changes, so check each browser's own documentation.

---

## How we got here

| When | What changed |
|---|---|
| January 2022 | The Web Store stopped accepting new public and unlisted MV2 extensions |
| Chrome 138 (mid-2025) | MV2 extensions were disabled by default for all users |
| Chrome 139 | Support for MV2 extensions was removed from Chrome |
| June 2026 | Chrome removed the flag that let users turn MV2 extensions back on |
| August 31, 2026 | All remaining MV2 extensions were removed from the Web Store |

The dates come from [Chrome's official MV2 support timeline](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline), with the June 2026 flag removal reported by [Android Authority](https://androidauthority.com/google-chrome-old-manifest-v2-extensions-delete-3685207).

---

## Where to start

**Your extension disappeared or stopped working, and you want to know why.**
Google's Manifest V3 changed how extensions run in the browser. It is a stricter platform with limits on background processes, data access, and remotely hosted code, and those limits are why tools like the original uBlock Origin no longer work in Chrome.

→ Read more: [What is Chrome Manifest V3 and Why Extensions Break](https://frontbuffer.net/tech/what-is-chrome-manifest-v3-and-why-extensions-break/)

**You want to know which of your extensions are still on MV2.**
You can check inside Chrome at `chrome://extensions`, where MV2 extensions have shown a warning banner. Developers can enable Developer Mode and inspect an extension's `manifest.json` to confirm its version.

→ Read more: [How to Check If Chrome Extensions Use Manifest V2](https://frontbuffer.net/tech/how-to-check-if-chrome-extensions-use-manifest-v2/)

**You need a replacement that works under the new rules.**
uBlock Origin Lite, AdGuard, and Adblock Plus have MV3 versions. Their filtering is more limited than the old MV2 versions, so how much that matters depends on how you use them. Browsers such as Firefox take a different approach, since they still support MV2.

→ Read more: [Best Manifest V3 Alternatives for Older Chrome Extensions](https://frontbuffer.net/tech/best-manifest-v3-alternatives-for-older-chrome-extensions/)

---

## Takeaway

If an MV2 extension still runs on your current Chrome, treat it as temporary. It won't update, you can't reinstall it from the Web Store, and a new laptop or a clean Chrome install won't bring it back. Check what you have, pick an MV3 replacement, and test it before you reinstall Chrome.

---
## Sources

- [Chrome for Developers — Manifest V2 support timeline](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline)
- [9to5Google — Google Chrome will remove older Manifest V2 extensions in August](https://9to5google.com/2026/07/08/google-chrome-will-remove-older-manifest-v2-extensions-in-august/)
- [Android Authority — Chrome Web Store to remove old Manifest V2 extensions](https://androidauthority.com/google-chrome-old-manifest-v2-extensions-delete-3685207)
- [Gigazine — Google removes Manifest V2 extensions from the Chrome Web Store](https://gigazine.net/gsc_news/en/20260901-manifest-v2-extensions)
