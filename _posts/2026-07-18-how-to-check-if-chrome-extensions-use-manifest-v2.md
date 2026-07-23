---
layout: single
title: "How to Check If Chrome Extensions Use Manifest V2"
date: 2026-07-18 10:00:00 +0900
categories: [tech]
tags: ["chrome extensions", "manifest v2", "check extension manifest version", "chrome developer mode"]
excerpt: "The Chrome extensions ecosystem has undergone one of the most significant architectural shifts in recent browser history. Google's multi-year phase-ou"
author_profile: false
read_time: true
share: true
---

Chrome 138 disabled Manifest V2 extensions for all standard users in July 2025, and the [Chrome Web Store is set to remove all remaining MV2 listings on August 31, 2026](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline). If an extension in your browser stopped working over the past year, it was almost certainly running on the legacy framework. Here is how to confirm which extensions are affected and what the deadline means going forward.

---

## The Architectural Shift: What Changed Between Manifest V2 and V3

Google's transition away from Manifest V2 represents a fundamental redesign of how browser extensions interact with core web technologies. According to [Google's official migration documentation](https://developer.chrome.com/docs/extensions/develop/migrate), Manifest V3 introduces strict structural requirements designed to enhance user security, system performance, and privacy.

Under the older Manifest V2 framework, extensions frequently utilized persistent background pages or event pages that remained active continuously, consuming system memory even when idle. Manifest V3 replaces these with modern service workers, moving background execution off the main thread to prevent extension code from degrading overall browser responsiveness.

The migration also alters how extensions manage security and data access. The newer platform completely removes support for remotely hosted code and the execution of arbitrary strings — all executable logic must now be bundled directly within the extension package. Network request handling has been overhauled as well: the legacy blocking web request API, which granted extensions broad access to sensitive user data and could slow page rendering, is replaced by the Declarative Net Request API, which shifts processing to the browser engine itself.

---

## How to Check If an Extension Uses Manifest V2

There are two methods available depending on whether you are an end user or a developer managing extension files directly.

### Method 1: Check via chrome://extensions (End Users)

The simplest way for regular Chrome users to identify legacy extensions is through the built-in extension management page. Since Chrome began rolling out the MV2 deprecation, the `chrome://extensions` page displays a **warning banner** for any installed extension still running on Manifest V2. To check:

1. Open Chrome and navigate to `chrome://extensions` in the address bar.
2. Look for any extensions showing a warning banner indicating they "will soon no longer be supported" or have already been disabled.
3. Extensions showing this banner are confirmed Manifest V2 add-ons.

Worth keeping in mind: as of Chrome 138, most MV2 extensions have already been automatically disabled for standard users. If an extension is still running in your browser today, it is almost certainly already Manifest V3 compliant.

### Method 2: Inspect the manifest.json File (Developers)

For developers managing extension source files directly, the most definitive check involves inspecting the core configuration file. Every Chrome extension includes a `manifest.json` file at its root:

1. Locate the root directory containing the extension's files.
2. Open `manifest.json` using any standard text editor.
3. Find the `"manifest_version"` key within the JSON structure.
   - A value of `2` confirms a **legacy Manifest V2** extension requiring migration.
   - A value of `3` confirms the extension meets the current **Manifest V3** standard.

For developers who need to assess large numbers of extensions at once, Google maintains an open-source [Extension Manifest Converter](https://github.com/GoogleChromeLabs/extension-manifest-converter) that parses legacy files and highlights structural compliance gaps. While it does not rewrite complex API calls or handle full service worker refactoring, it serves as a useful baseline diagnostic tool.

---

## The August 2026 Deadline: What It Means for Users and Developers

The deprecation timeline has two remaining milestones that affect different audiences:

- **July 28, 2026 (Chrome 151):** The final developer flags that allowed MV2 re-enabling in Chrome are deleted. After this date, no mechanism exists to run MV2 extensions in Chrome under any configuration.
- **August 31, 2026:** All remaining MV2 extension listings are permanently removed from the Chrome Web Store. Extensions already installed on Chrome 138 or earlier may remain in the browser, but will receive no further updates and cannot be reinstalled if removed.

For practical purposes, if an extension still functions in Chrome today, it has already been updated to Manifest V3.

---

## Cross-Browser Implications: Chromium-Based Browsers

Because the Chromium engine underpins multiple major browsers, this architectural migration extends beyond Chrome itself. Browsers built on Chromium — including Microsoft Edge, Opera, and Brave — share the same underlying extension architecture, meaning add-ons built for Chrome's ecosystem face equivalent long-term structural pressures.

While some Chromium-based browsers have historically supported legacy APIs longer than Google's own timeline, the structural shift in the engine's codebase means developers must eventually align with the Manifest V3 service worker architecture. Add-ons designed for specialized use cases — video management utilities, social media modifiers, or developer workflow tools — face identical performance and security constraints if left unmigrated.

---

## Migration Best Practices for Developers

When converting a legacy extension to the modern standard, Google's official guidance recommends prioritizing stability over new features during the transition:

- **Isolate structural changes:** Focus exclusively on compatibility during migration. Adding capabilities that require new permissions can trigger unexpected permission warnings for existing users.
- **Transition to service workers:** Background and event pages must be phased out entirely. DOM operations, window references, and incompatible API calls must be relocated to dedicated offscreen documents.
- **Refactor network listeners:** Any blocking web request infrastructure must be rewritten using the Declarative Net Request API, reducing data access permissions while shifting processing to the browser.
- **Use phased rollouts:** Publish the updated extension to a limited audience first to confirm stability before deploying globally.

For users discovering that a favorite extension has been disabled, the Chrome Web Store provides recommended Manifest V3 alternatives where available for affected add-ons.

---

Sources:

- [Google Chrome: Manifest V2 Deprecation Timeline](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline)
- [Google Developer Migration Overview](https://developer.chrome.com/docs/extensions/develop/migrate)
- [Extension Manifest Converter (GitHub)](https://github.com/GoogleChromeLabs/extension-manifest-converter)
- [9to5Google: Chrome will remove older Manifest V2 extensions in August](https://9to5google.com/2026/07/08/google-chrome-will-remove-older-manifest-v2-extensions-in-august/)
