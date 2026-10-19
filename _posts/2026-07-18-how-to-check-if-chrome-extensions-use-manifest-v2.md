---
layout: single
title: "How to Check If a Chrome Extension Uses Manifest V2"
date: 2026-07-18 10:00:00 +0900
last_modified_at: 2026-10-16 00:00:00 +0900
categories: [tech]
tags: ["chrome extensions", "manifest v2", "check extension manifest version", "chrome developer mode"]
excerpt: "Chrome 138 disabled Manifest V2 extensions in July 2025, and the Web Store dropped the rest on August 31, 2026. How to tell which of yours were affected."
header:
  image: https://images.frontbuffer.net/posts/how-to-check-if-chrome-extensions-use-manifest-v2/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

Whether an extension still runs depends on two things: the Manifest version it was built on and the Chrome version you use. [Chrome's official timeline](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline) says Chrome 138 disabled Manifest V2 (MV2) extensions everywhere on July 24, 2025, and that MV2 extensions cease to function for anyone upgrading to Chrome 139 or later. It also says all remaining MV2 extensions were removed from the Chrome Web Store on August 31, 2026. This page explains how to check where your extensions stand.

*Checked October 16, 2026 against Chrome's timeline page, last updated September 9, 2026. Nothing here was tested in a browser.*

---

## Where MV2 extensions stand today

| Your browser | What happens to MV2 extensions |
|---|---|
| Chrome 139 or newer | They do not run, per Chrome's timeline |
| Chrome 138 or earlier | Extensions installed before keep running, but they cannot update and cannot be reinstalled if removed, per Chrome |
| Firefox | Mozilla says it keeps MV2 [alongside Manifest V3](https://blog.mozilla.org/en/products/firefox/firefox-manifest-v3-adblockers/) |
| Brave and Edge | [BetaNews reports](https://betanews.com/article/firefox-brave-ublock-origin-chrome-edge/) that Brave said it hosts uBlock Origin and other MV2 extensions on its own servers, and that Edge is phasing MV2 out |

If an extension stopped working after you updated Chrome, the likely reason is that it was an MV2 extension. That is an inference from the timeline, not something Chrome tells you in the extension list, so confirm it with the checks below.

---

## How to check as a regular user

Open `chrome://extensions` in the address bar. Chrome's timeline describes what that page showed during the phase-out. From June 2024 some users saw a warning banner there saying that some MV2 extensions would soon no longer be supported, and from October 2024 Chrome began disabling installed MV2 extensions in the stable channel and sent users to the Web Store to see recommended MV3 alternatives. The sources checked do not say whether those banners still appear in current Chrome versions.

A practical way to read the page now:

1. Look for extensions that are turned off or flagged as unavailable.
2. Search the extension's name in the Chrome Web Store. If the listing is gone, it may have been one of the MV2 extensions removed on August 31, which is an inference rather than a Chrome statement.
3. Look for an MV3 version from the same developer. For ad blockers, see [our guide to MV3 alternatives](https://frontbuffer.net/tech/best-manifest-v3-alternatives-for-older-chrome-extensions/).

---

## How to check the manifest file

If you have an extension's files, or you are the developer, open its `manifest.json` and find the `"manifest_version"` key. A value of 2 means a Manifest V2 extension, and a value of 3 means Manifest V3. Chrome's [migration guide](https://developer.chrome.com/docs/extensions/develop/migrate) has a step for updating the manifest.

---

## What changed between MV2 and MV3

[Chrome's own overview](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3) lists three main changes:

- **Service workers instead of long-lived background pages.** MV2 extensions had a background page that took up resources even when the extension was not running. In MV3, the background context runs only when needed.
- **No remotely hosted code.** An extension can only execute JavaScript included in its own package, which is subject to Chrome Web Store review.
- **A new way to modify network requests.** Chrome deprecated the blocking version of the webRequest API and offers the declarativeNetRequest API as what it calls a safer alternative for many use cases. Extension makers, especially ad blockers, say it is more limiting. Our [hub page](https://frontbuffer.net/tech/google-chrome-manifest-v2-migration_HUB/) and [MV3 explainer](https://frontbuffer.net/tech/what-is-chrome-manifest-v3-and-why-extensions-break/) cover both views.

---

## If you are a developer

Chrome's [migration overview](https://developer.chrome.com/docs/extensions/develop/migrate) and checklist are the reference. There is also an open-source [Extension Manifest Converter](https://github.com/GoogleChromeLabs/extension-manifest-converter) in the GoogleChromeLabs GitHub organization. Its repository says it helps convert an extension to MV3 using search-and-replace changes, that it does not fully automate the conversion, and that it is not an official Google product. The repository was archived on April 19, 2026 and is now read-only, so treat it as a starting point at most.

---

## Which guide to read next

- **Replacing an ad blocker:** [Best Manifest V3 Alternatives for Older Chrome Extensions](https://frontbuffer.net/tech/best-manifest-v3-alternatives-for-older-chrome-extensions/)
- **Why extensions broke:** [What is Chrome Manifest V3 and Why Extensions Break](https://frontbuffer.net/tech/what-is-chrome-manifest-v3-and-why-extensions-break/)
- **The full timeline:** [Chrome Manifest V2 Is Dead: What Happened and What to Use Instead](https://frontbuffer.net/tech/google-chrome-manifest-v2-migration_HUB/)

---

Sources:

- [Manifest V2 support timeline, Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline)
- [What is Manifest V3, Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3)
- [Migrate to Manifest V3, Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/migrate)
- [Extension Manifest Converter, GoogleChromeLabs on GitHub](https://github.com/GoogleChromeLabs/extension-manifest-converter)
- [Mozilla's approach to Manifest V3, Mozilla Blog](https://blog.mozilla.org/en/products/firefox/firefox-manifest-v3-adblockers/)
- [Firefox and Brave keep uBlock Origin as Chrome and Edge phase out support, BetaNews](https://betanews.com/article/firefox-brave-ublock-origin-chrome-edge/)
- [Google Chrome will remove older Manifest V2 extensions in August, 9to5Google](https://9to5google.com/2026/07/08/google-chrome-will-remove-older-manifest-v2-extensions-in-august/)
