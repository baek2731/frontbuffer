---
layout: single
title: 'What to Use Instead of uMatrix in 2026'
date: 2026-10-16 14:27:00 +0000
categories: [tech]
tags: ["guide", "umatrix", "use", "instead"]
excerpt: 'uMatrix is dead. In 2026, the best replacement for advanced users is uBlock Origin in advanced mode, but it only fully works on Firefox and Brave.'
author_profile: false
read_time: true
share: true
---

If you used uMatrix to decide which scripts, frames and third-party domains a site may load, the practical replacement is uBlock Origin in advanced mode. The catch is that it runs fully only on some browsers, and Chrome is not one of them.

## What happened to uMatrix

Its developer, Raymond Hill, [archived the uMatrix repository in 2020](https://alternativeto.net/news/2020/9/developer-of-ublock-origin-has-ceased-development-on-umatrix), saying he would not spend more time on it and that anyone could fork it under a new name. It has been unmaintained since, so even where an old copy still loads, it gets no fixes.

Security researcher Tavis Ormandy notes that [uMatrix's features were more or less a subset of uBlock Origin's](https://lock.cmpxchg8b.com/umatrix.html), which is why users were told to move to uBO. That advice holds only where the browser still runs the full uBO.

## Which browsers still run the full uBlock Origin

| Browser | Full uBO? | What the sources say |
|---|---|---|
| Chrome | No | Chrome's timeline says [Manifest V2 was disabled everywhere with Chrome 138 on July 24, 2025](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline), and lists August 31, 2026 as the date all remaining Manifest V2 extensions are removed from the Chrome Web Store |
| Firefox | Yes | Mozilla keeps Manifest V2 [alongside Manifest V3 and continues to support the blocking webRequest API](https://blog.mozilla.org/en/products/firefox/firefox-manifest-v3-adblockers/). On August 10, 2026 the Firefox account posted that [support for uBlock Origin is not going anywhere](https://betanews.com/article/firefox-brave-ublock-origin-chrome-edge/) |
| Brave | For now | Brave said it hosts uBlock Origin and other Manifest V2 extensions on its own servers, per [BetaNews](https://betanews.com/article/firefox-brave-ublock-origin-chrome-edge/). [Chipp.in](https://chipp.in/news/firefox-will-continue-to-support-ublock-origin-says-mozilla/) adds that Brave plans to continue support for some extensions only, including uBlock Origin |
| Edge | Ending | Microsoft announced it is ending Manifest V2 support. Mezha reports [beta versions first and stable versions by the end of the year](https://mezha.ua/en/news/firefox-keeps-full-ublock-origin-support-314083/amp/) |

## Rebuild the matrix in uBlock Origin

This works in Firefox, and in Brave while it keeps hosting the extension. The steps follow the uBlock Origin wiki's [medium mode page](https://github.com/gorhill/uBlock/wiki/Blocking-mode:-medium-mode), which the wiki calls optimal for advanced users. That page was last edited in 2022, so the popup may look slightly different today.

1. Install uBlock Origin from your browser's add-on store.
2. In the dashboard's **Settings** pane, check **I am an advanced user**. The [wiki](https://github.com/gorhill/uBlock/wiki/Advanced-user-features) says this makes dynamic filtering available, and warns to enable it at your own risk because novices can easily break filtering with it.
3. Keep uBO's filter lists enabled. The medium mode page lists EasyList, Peter Lowe's Ad server list, EasyPrivacy and the Online Malicious URL Blocklist.
4. In the **My rules** pane, add these two rules:
 - `* * 3p-script block`
 - `* * 3p-frame block`
5. Reload a site. Third-party scripts and frames are now blocked by default, while passive third-party resources such as images and CSS are not. A blue badge on the toolbar button shows that medium mode is active.

The wiki describes this as roughly similar to an ad blocker with many filter lists plus NoScript with first-party scripts trusted, with the difference that you can allow or block scripts per site by clicking.

### When a site breaks

Expect broken pages at first. The wiki says the breakage drops as you build rules for the sites you visit. To fix a site, the wiki says to [set a local noop rule](https://github.com/gorhill/uBlock/wiki/Blocking-mode:-medium-mode) on the third-party script cell, and optionally the third-party frames cell, in the popup. Click the padlock to make the rule permanent. The [quick guide](https://github.com/gorhill/uBlock/wiki/Dynamic-filtering:-quick-guide) says local rules override global ones, so medium mode stays in force everywhere else.

Rules from an existing uMatrix setup are not covered here. Whether they can be imported was not checked.

## If you stay on Chrome

The Manifest V3 version, uBlock Origin Lite, cannot do what uMatrix did. Its FAQ explains that the declarativeNetRequest API [cannot apply rules by the page you are on](https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-(FAQ)), so capabilities such as dynamic filtering cannot be supported. It also says that building dynamic filtering on webRequest would wake the service worker constantly and defeat the extension's efficiency goal. The FAQ lists more capabilities that cannot be ported to MV3.

On Chrome you have two honest options: accept a plain blocker with no per-site matrix, or keep a second browser for the sites where you want the control.

## Another option

Ormandy also published a replacement extension for Chrome and calls it [clearly in a prototype state](https://lock.cmpxchg8b.com/umatrix.html). Treat it as something to review before installing, not a drop-in replacement.

## Which to pick

| Your browser | Pick |
|---|---|
| Firefox | uBlock Origin with advanced mode and the two rules above |
| Brave | The same, while Brave keeps hosting the extension |
| Chrome | uBlock Origin Lite, with no matrix, or a second browser for matrix control |
| Edge | Plan a move, since Manifest V2 support is ending |

Checked October 15, 2026 against the sources listed below. Nothing here was tested hands-on.

---
Sources:
- [Developer of uBlock Origin has ceased development on uMatrix, AlternativeTo](https://alternativeto.net/news/2020/9/developer-of-ublock-origin-has-ceased-development-on-umatrix)
- [Replacing uMatrix, Tavis Ormandy](https://lock.cmpxchg8b.com/umatrix.html)
- [Manifest V2 support timeline, Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline)
- [Mozilla's approach to Manifest V3, Mozilla Blog](https://blog.mozilla.org/en/products/firefox/firefox-manifest-v3-adblockers/)
- [Firefox and Brave keep uBlock Origin as Chrome and Edge phase out support, BetaNews](https://betanews.com/article/firefox-brave-ublock-origin-chrome-edge/)
- [Firefox will continue to support uBlock Origin, says Mozilla, Chipp.in](https://chipp.in/news/firefox-will-continue-to-support-ublock-origin-says-mozilla/)
- [Firefox keeps full uBlock Origin support, Mezha](https://mezha.ua/en/news/firefox-keeps-full-ublock-origin-support-314083/amp/)
- [Blocking mode: medium mode, uBlock Origin wiki](https://github.com/gorhill/uBlock/wiki/Blocking-mode:-medium-mode)
- [Advanced user features, uBlock Origin wiki](https://github.com/gorhill/uBlock/wiki/Advanced-user-features)
- [Dynamic filtering: quick guide, uBlock Origin wiki](https://github.com/gorhill/uBlock/wiki/Dynamic-filtering:-quick-guide)
- [Frequently asked questions, uBlock Origin Lite wiki](https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-(FAQ))
