---
layout: single
title: "Why Chrome Extensions Stopped Working: Manifest V3 Explained"
date: 2026-07-20 10:00:00 +0900
last_modified_at: 2026-10-16 00:00:00 +0900
categories: [tech]
tags: ["chrome extensions", "manifest v3", "mv2 deprecation", "declarative net request"]
excerpt: 'Chrome disabled Manifest V2 extensions, including the original uBlock Origin, in 2025. What MV3 changed: service workers, no remote code and declarative rules.'
header:
  image: https://images.frontbuffer.net/posts/what-is-chrome-manifest-v3-and-why-extensions-break/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

Chrome extensions broke because Chrome stopped running the older Manifest V2 (MV2) format, and some extensions could not be rebuilt the way Manifest V3 (MV3) requires. [Chrome's timeline](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline) says Chrome 138 disabled MV2 extensions for all users on July 24, 2025, MV2 extensions cease to function for anyone on Chrome 139 or later, and the Web Store removed all remaining MV2 extensions on August 31, 2026. This article explains what MV3 changed and why ad blockers were hit hardest.

*Checked October 16, 2026 against Chrome's own pages and press reports. Nothing here was tested in a browser.*

---

## What Chrome says MV3 changed

[Chrome's overview of Manifest V3](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3) lists three main changes. Its stated goal is to improve the privacy, security and performance of extensions.

- **Service workers instead of a long-lived background page.** MV2 extensions had a background page that took up resources even when the extension was not running. In MV3, the background context runs only when needed. Code that depended on a persistent page has to be reworked, and Chrome's [migration guide](https://developer.chrome.com/docs/extensions/develop/migrate) covers how.
- **No remotely hosted code.** An extension can only execute JavaScript that is included in its package, and that package is subject to Chrome Web Store review. Chrome says remote code presented security risks by allowing unreviewed code to run.
- **A different way to modify network requests.** Chrome deprecated the blocking version of the webRequest API, which required extensions to proxy all network traffic and came at a performance and privacy cost. The declarativeNetRequest API is what Chrome calls a safer alternative for many use cases.

Chrome's page also mentions support for promise-based methods among the other changes.

---

## Why ad blockers were hit hardest

The third change is the one that matters for ad blockers. Under the old API an extension could inspect each request and decide what to do with it. Under declarativeNetRequest, the extension hands Chrome a set of rules in advance and the browser applies them.

Chrome describes this as safer. The blocker makers describe it as a restriction, and both statements match their sources:

- The uBlock Origin Lite [FAQ](https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-%28FAQ%29) says features such as dynamic filtering cannot be supported under MV3, because declarativeNetRequest cannot apply rules according to the page you are on. It adds that building dynamic filtering on webRequest would wake the extension's service worker constantly and defeat the point of the Lite version. That is why the original uBlock Origin could not simply be updated.
- [AdGuard's 2022 blog post](https://adguard.com/blog/adguard-mv3.html) about its first MV3 prototype says the syntax of declarative rules severely limits what an extension can do. It also reports the rule limits Chrome set at that time: at least 30,000 static rules guaranteed per extension, 330,000 across a user's extensions, and 5,000 dynamic rules. Chrome may have changed those numbers since.
- eyeo, which makes Adblock Plus, says Chrome enforces limits on rulesets and on static and dynamic rules, and that its engineers had to work around them. See [eyeo's MV3 write-up](https://resources.eyeo.com/mv3-ready).

---

## MV2 versus MV3 at a glance

| | Manifest V2 | Manifest V3 |
|---|---|---|
| Background code | Long-lived background page | Service worker that runs only when needed |
| Remote code | Allowed | Not allowed. Only code in the package runs |
| Network requests | Blocking webRequest listeners | declarativeNetRequest rules |
| API style | Callback-based | Promise-based methods supported |

---

## How we got here

Chrome stopped accepting new public MV2 extensions in January 2022 and began the phase-out in June 2024. It disabled MV2 extensions by default for all users on March 31, 2025, and disabled them everywhere with Chrome 138. [Android Authority](https://www.androidauthority.com/google-chrome-old-manifest-v2-extensions-delete-3685207/) and [9to5Google](https://9to5google.com/2026/07/08/google-chrome-will-remove-older-manifest-v2-extensions-in-august/) report that Chrome also stripped a loophole that had let users re-enable older extensions in mid-2026. Chrome's own timeline does not list that step. Our [hub page](https://frontbuffer.net/tech/google-chrome-manifest-v2-migration_HUB/) has the full table.

If an extension works in Chrome today, it is running on MV3, because Chrome 139 and later do not run MV2 extensions. Extensions installed on Chrome 138 or earlier keep running but cannot update or be reinstalled, according to Chrome.

---

## Other browsers

Mozilla says it keeps MV2 alongside MV3 and [continues to support the blocking webRequest API](https://blog.mozilla.org/en/products/firefox/firefox-manifest-v3-adblockers/), so the full uBlock Origin runs on Firefox. [BetaNews reports](https://betanews.com/article/firefox-brave-ublock-origin-chrome-edge/) that Brave said it hosts uBlock Origin and other MV2 extensions on its own servers, and that Edge is phasing MV2 out. For setting up uBlock Origin's advanced mode in Firefox, see [What to Use Instead of uMatrix in 2026](https://frontbuffer.net/tech/what-to-use-instead-of-umatrix-in-2026/).

---

## For developers

Chrome's migration overview and checklist are the reference. A GoogleChromeLabs [Extension Manifest Converter](https://github.com/GoogleChromeLabs/extension-manifest-converter) exists on GitHub, but its repository says it uses search-and-replace changes, does not fully automate the work, and is not an official Google product. It was archived on April 19, 2026 and is read-only.

---

For replacements, see [Best Manifest V3 Alternatives for Older Chrome Extensions](https://frontbuffer.net/tech/best-manifest-v3-alternatives-for-older-chrome-extensions/). To check whether an extension is on MV2, see [How to Check If a Chrome Extension Uses Manifest V2](https://frontbuffer.net/tech/how-to-check-if-chrome-extensions-use-manifest-v2/).

---

Sources:

- [Manifest V2 support timeline, Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline)
- [What is Manifest V3, Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3)
- [Migrate to Manifest V3, Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/migrate)
- [Frequently asked questions, uBlock Origin Lite wiki](https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-%28FAQ%29)
- [AdGuard publishes the world's first ad blocker built on Manifest V3, AdGuard](https://adguard.com/blog/adguard-mv3.html)
- [MV3 ready, eyeo](https://resources.eyeo.com/mv3-ready)
- [Google is about to delete some of your favorite Chrome extensions forever, Android Authority](https://www.androidauthority.com/google-chrome-old-manifest-v2-extensions-delete-3685207/)
- [Google Chrome will remove older Manifest V2 extensions in August, 9to5Google](https://9to5google.com/2026/07/08/google-chrome-will-remove-older-manifest-v2-extensions-in-august/)
- [Mozilla's approach to Manifest V3, Mozilla Blog](https://blog.mozilla.org/en/products/firefox/firefox-manifest-v3-adblockers/)
- [Firefox and Brave keep uBlock Origin as Chrome and Edge phase out support, BetaNews](https://betanews.com/article/firefox-brave-ublock-origin-chrome-edge/)
- [Extension Manifest Converter, GoogleChromeLabs on GitHub](https://github.com/GoogleChromeLabs/extension-manifest-converter)
