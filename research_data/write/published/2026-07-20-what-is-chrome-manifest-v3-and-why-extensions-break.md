---
layout: single
title: "What is Chrome Manifest V3 and Why Extensions Break"
date: 2026-07-20 10:00:00 +0900
categories: [tech]
tags: ["chrome extensions", "manifest v3", "mv2 deprecation", "declarative net request"]
excerpt: "For millions of Chrome users, the sudden disappearance of familiar browser add-ons over the past year came without much warning. Google's transition t"
author_profile: false
read_time: true
share: true
---

For millions of Chrome users, the sudden disappearance of familiar browser add-ons over the past year came without much warning. Google's transition to Manifest V3 — the newest version of the Chrome Extensions platform — fundamentally overhauled how browser add-ons interact with the core engine. The migration is now largely complete: as of July 2025, Chrome 138 permanently disabled all Manifest V2 extensions for standard users, and the [Chrome Web Store is set to remove all remaining MV2 listings on August 31, 2026](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline). This explainer breaks down what changed, why it caused disruptions, and what the shift means going forward.

---

## What Manifest V3 Actually Changed

Manifest V3 is not a minor update — it is a complete architectural rewrite of the rules governing how Chrome extensions are built and what they are permitted to do. Google introduced it to address three core problems with the legacy Manifest V2 framework: performance overhead from always-on background processes, privacy risks from extensions with excessive data access, and security vulnerabilities from extensions that executed code fetched from external servers.

The changes introduced by Manifest V3 fall into four interconnected categories, each of which required developers to rebuild core parts of their extensions from scratch.

---

## The Shift to Service Workers: Why Background Processes Changed

One of the most disruptive changes involves how extensions handle background tasks. Under Manifest V2, extensions relied on persistent background pages or event pages — processes that ran continuously, consuming system memory even when completely idle.

According to [Google's official migration documentation](https://developer.chrome.com/docs/extensions/develop/migrate), Manifest V3 replaces these persistent environments entirely with **service workers**: ephemeral, event-driven processes that spin up when needed and shut down when idle. This keeps background code off the main thread and prevents extensions from degrading browser performance over time.

The catch: service workers have no persistent DOM context. Any extension that previously used the DOM, the `window` object, or specific extension APIs in its background process had to be substantially rewritten to use dedicated **offscreen documents** — lightweight, invisible pages that handle those operations in isolation.

---

## The End of Blocking Web Requests: The Core Reason Ad Blockers Broke

The single change most responsible for disrupting popular extensions — particularly ad blockers and privacy tools — is the removal of the blocking web request API.

Under Manifest V2, extensions could intercept and modify network traffic in real time using blocking web request listeners. This gave them enormous power, but as [Chrome's net request documentation](https://developer.chrome.com/docs/extensions/develop/migrate/blocking-web-requests) explains, it also required extensions to have excessive access to sensitive user data and could significantly degrade page load performance.

Manifest V3 replaces this with the **Declarative Net Request API**, which requires extensions to declare filtering rules upfront. The browser executes those rules directly, without passing raw network data through the extension. The result: less data exposure and better performance — but also a hard cap on the number of rules an extension can apply, and no ability to filter requests dynamically based on real-time conditions.

This is why tools like the original uBlock Origin could not simply be updated for Manifest V3. The dynamic, real-time filtering they depended on no longer exists as a permitted extension capability.

---

## Eliminating Remotely Hosted Code: The Security Overhaul

Legacy extensions frequently executed JavaScript fetched from external servers — a capability that created serious security exposure. If an external server was compromised, an attacker could push malicious code into a trusted extension without any browser store review.

Manifest V3 closes this gap entirely. As documented in [Chrome's security improvement guide](https://developer.chrome.com/docs/extensions/develop/migrate/improve-security), the platform now enforces a strict Content Security Policy that prohibits remotely hosted code and forbids the execution of arbitrary strings. Every line of code an extension executes must be packaged locally within the extension bundle and reviewed during the Web Store submission process.

---

## The Deprecation Timeline: What Already Happened and What's Left

The Manifest V2 phase-out unfolded over several years, with the most significant milestones now behind us:

- **July 24, 2025 (Chrome 138):** MV2 extensions permanently disabled for all standard Chrome users. This is when most users noticed their ad blockers and other tools stop working.
- **August 2025 (Chrome 139):** Enterprise users who had received an exemption via the `ExtensionManifestV2Availability` policy also lost MV2 support, as the policy itself was removed from Chrome.
- **June 30, 2026 (Chrome 150):** The first developer flag allowing MV2 re-enabling was deleted.
- **July 28, 2026 (Chrome 151):** The final developer flag is deleted, closing every remaining workaround.
- **August 31, 2026:** All remaining MV2 extension listings are permanently removed from the Chrome Web Store.

As of July 2026, if an extension works in Chrome today, it is already Manifest V3 compliant. The August deadline affects only Chrome Web Store listings — not extensions already installed in browsers running Chrome 138 or earlier, which will simply stop receiving updates and become permanently orphaned.

---

## Cross-Browser Implications: Chrome Extensions Opera and Chromium Alternatives

Because the Chromium engine underpins Microsoft Edge, Opera, Brave, and others, the Manifest V3 transition extends beyond Chrome itself. The comparison below summarizes what changed across the framework:

| Feature Area | Manifest V2 | Manifest V3 |
| --- | --- | --- |
| **Background Architecture** | Persistent background/event pages | Ephemeral service workers + offscreen documents |
| **Network Modification** | Blocking Web Request API | Declarative Net Request API (static rules) |
| **Code Execution** | Remotely hosted code permitted | Local bundles only; enhanced CSP |
| **API Compliance** | Legacy synchronous APIs | Updated modern equivalents |

Firefox remains the notable exception among major browsers: Mozilla has explicitly committed to continuing support for both MV2 and MV3 extensions, meaning the full original uBlock Origin still runs without restriction on Firefox.

---

## Developer Transition Tools

For developers still migrating legacy extensions, Google provides an open-source [Extension Manifest Converter on GitHub](https://github.com/GoogleChromeLabs/extension-manifest-converter) that handles basic `manifest.json` structural updates. It does not automate complex API rewrites, but serves as a useful starting point.

Google's official guidance recommends keeping feature sets identical during migration rather than introducing new functionality — new permissions added during transition can trigger unexpected user-facing permission warnings and complicate the update path for existing installs.

---

Sources:

- [Google Chrome: Manifest V2 Deprecation Timeline](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline)
- [Google Chrome Developer Migration Guide](https://developer.chrome.com/docs/extensions/develop/migrate)
- [Chrome: Declarative Net Request API](https://developer.chrome.com/docs/extensions/develop/migrate/blocking-web-requests)
- [Chrome: Improve Extension Security](https://developer.chrome.com/docs/extensions/develop/migrate/improve-security)
- [Extension Manifest Converter (GitHub)](https://github.com/GoogleChromeLabs/extension-manifest-converter)
- [9to5Google: Chrome will remove older Manifest V2 extensions in August](https://9to5google.com/2026/07/08/google-chrome-will-remove-older-manifest-v2-extensions-in-august/)