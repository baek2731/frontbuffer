---
layout: single
title: 'uBlock Origin Lite: Filtering Modes, Settings and Limits'
date: 2026-10-23 14:43:00 +0000
last_modified_at: 2026-10-28 00:00:00 +0000
categories: [tech]
tags: ["guide", "ublock-origin-lite", "ublock-origin", "chrome-extensions"]
excerpt: 'uBlock Origin Lite''s filtering modes, per-site permissions and popup tools, plus what it cannot do compared with uBlock Origin, from the project''s own pages.'
header:
  image: https://images.frontbuffer.net/posts/ublock-origin-lite-filtering-modes-settings-and-limits/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

uBlock Origin Lite (uBOL) is the Manifest V3 content blocker that Raymond Hill, the developer of uBlock Origin, built for browsers where the full extension no longer runs. It is not a drop-in copy of the original. The project's own FAQ says Lite is too different from uBlock Origin (uBO) to count as an automatic replacement, and that whether it meets your expectations depends on the sites you visit and how you set it up.

*Checked October 22, 2026 against the uBOL project's FAQ (last edited August 24, 2026), Quick guide (September 5, 2026) and Troubleshooting page (July 28, 2026). On October 28, 2026 we re-opened the FAQ, which had not changed, and the Edge and Firefox store listings. Nothing here was tested in a browser.*

## Install

The project's FAQ links the [uBlock Origin Lite listing in the Chrome Web Store](https://chromewebstore.google.com/detail/ublock-origin-lite/ddkjiahejlhfcafbddmgiahcphecmpfh). Lite also has its own listings in the [Microsoft Edge Add-ons store](https://microsoftedge.microsoft.com/addons/detail/ublock-origin-lite/cimighlppcgcoapaliogpjjdehbnofhn) and on [Mozilla's add-on site](https://addons.mozilla.org/ia/android/addon/ublock-origin-lite/), including a version for Firefox for Android. The Troubleshooting page shows permission settings for Chromium browsers, Firefox and Safari on macOS and iOS.

## The filtering modes

The filtering mode is the main setting in Lite, and you can change it per site. According to the project's pages:

- **Disabled for a site:** move the filtering mode slider completely to the left while you are on that site.
- **Basic:** still filters network requests, but applies no cosmetic or scriptlet filters.
- **Optimal:** the intended default. Some ad placeholders may remain on a given site.
- **Complete:** set a site to Complete to get rid of leftover placeholders. The FAQ adds that Lite applies no generic cosmetic filtering by default, and you have to raise the mode to Complete to get it.

A sensible starting point is to leave the default on Optimal and raise only the sites that need it.

## Site access permission

If you do not give Lite permission to read and change data on all websites by default, the default filtering mode switches back to Basic, according to the Troubleshooting page. The page has screenshots of where this permission lives in each browser, and the menu names differ between browsers.

## Tools in the popup

The Quick guide describes two tools:

- **Remove an element:** hides an element temporarily and tries to restore scrolling on pages where scrolling is disabled. Reloading the page brings the element back.
- **Create a custom filter:** hides an element permanently, every time you visit the site. You can review, edit and delete these filters in the Custom filters pane of the dashboard.

## Filter lists and custom filters

The FAQ explains that Lite has no filter lists as such. It ships declarative rulesets compiled from filter lists when the extension package is built, so those built-in rulesets update only when the extension itself updates. The same section of the FAQ says Lite never makes network requests to remote servers. A note added in June 2026 says custom filters and external filter lists are now available in a way that keeps Lite's reliability and efficiency. We did not confirm the menu steps for external lists, or whether that note changes the statement about network requests, so look in the dashboard and the project's pages.

## What Lite cannot do

Per the FAQ:

- **No dynamic filtering.** A newer Chromium condition makes parts of it theoretically possible, but the maintainer says it would still require constantly waking the service worker, which works against Lite's efficiency goal.
- **Some filter options cannot be converted**, such as `strict1p` and `strict3p`, regex-based `removeparam=`, and `redirect-rule=`.
- **It is generally less effective** on sites that use anti-content-blocker measures, and at avoiding site breakage, because many filters cannot become declarative rules.
- **CNAME uncloaking** is not supported, and the FAQ says no declarative implementation supports it at the time of writing.
- **Rule limits are not a problem in practice.** The default ruleset hovers around 17,000 rules in Optimal or Complete mode, against a guaranteed minimum of 30,000 and a 330,000 global limit in Chromium.
- **Do not run another content blocker alongside it**, for the same reasons you should not do so with uBO.

## If a site is not being filtered

1. Check that the site is not set to the disabled position.
2. Try Optimal. If empty ad spaces remain, try Complete for that site.
3. Confirm Lite has permission to read and change data on all sites.
4. On Safari, make sure Content Blockers are allowed, as the Troubleshooting page describes.
5. Disable your other extensions and open the site in a new tab. The FAQ notes that other non-blocking extensions can interfere.

## Where it fits

Lite suits people who want an install-and-forget blocker on Chrome or Edge. If you relied on uBO's dynamic filtering, Lite will feel different. Our guides cover [what to use as the Manifest V2 removal reaches Chrome](https://frontbuffer.net/tech/best-manifest-v3-alternatives-for-older-chrome-extensions/) and [what to use instead of uMatrix](https://frontbuffer.net/tech/what-to-use-instead-of-umatrix-in-2026/).

---
Sources:
- [Frequently asked questions (FAQ), uBOL-home Wiki](https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-%28FAQ%29)
- [Quick guide, uBOL-home Wiki](https://github.com/uBlockOrigin/uBOL-home/wiki/Quick-guide)
- [Troubleshooting, uBOL-home Wiki](https://github.com/uBlockOrigin/uBOL-home/wiki/Troubleshooting)
- [uBlock Origin Lite, Microsoft Edge Add-ons](https://microsoftedge.microsoft.com/addons/detail/ublock-origin-lite/cimighlppcgcoapaliogpjjdehbnofhn)
- [uBlock Origin Lite by Raymond Hill, Firefox Browser Add-ons](https://addons.mozilla.org/ia/android/addon/ublock-origin-lite/)
