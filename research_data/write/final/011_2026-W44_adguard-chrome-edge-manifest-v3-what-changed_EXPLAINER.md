# AdGuard on Chrome and Edge After Manifest V3: What Changed

AdGuard's browser extension now runs on Manifest V3 (MV3) in Chrome, and AdGuard has added an MV3 version for Microsoft Edge. AdGuard says most existing Chrome users need to do nothing. What does change, by AdGuard's own account, is that the browser applies a prebuilt ruleset, the number of active rules is limited, some rules cannot be converted exactly, and most filter updates now arrive with the extension itself.

*Checked October 28, 2026 against AdGuard's blog and its browser extension release notes on GitHub. Nothing here was tested in a browser.*

## Chrome

In a post about Chrome removing its Manifest V2 extension from the Web Store, [AdGuard says](https://adguard.com/en/blog/adguard-adblocker-manifestv2-removal.html) it rebuilt AdGuard Ad Blocker for MV3 and that the MV3 version became its primary Chrome extension in September 2024. It describes tools it built to convert traditional filters into MV3 rules, and an engine of its own that it kept for hiding ads and other elements on pages. It also says it found ways to deliver urgent fixes within MV3's allowance for dynamic rules, and that custom filters in MV3 can again update independently of the extension.

## Edge

AdGuard's [5.5.3.3 release notes](https://github.com/AdguardTeam/AdguardBrowserExtension/releases/tag/v5.5.3.3) say AdGuard's MV3 extension was added to Microsoft Edge, and that MV2 ad blockers no longer appear in Edge Add-ons search results. The notes tie this to Microsoft's policy on moving away from MV2 extensions, announced in August, and say AdGuard is not leaving the store.

To use custom filters and user rules in Edge, the same notes say to turn on **Allow user scripts** for the AdGuard Browser Extension: find AdGuard in Edge's extensions list, click **Details**, and switch it on.

## What MV3 changes in practice

AdGuard's release notes put it this way. With MV2 the extension sees each network request in real time and decides what to block. With MV3 the browser receives a prebuilt ruleset and applies it. That means:

- the number of active rules is limited
- some traditional filtering rules cannot be converted exactly
- most filter updates ship with the extension, so they can take longer

AdGuard adds that everyday filtering stays close to MV2 for most people, but the browser now makes more of the decisions and keeping behavior close to MV2 takes more work.

The underlying limits are the ones that apply to every MV3 blocker. The uBOL project's FAQ gives a guaranteed minimum of 30,000 static rules per extension and a global limit of 330,000 in Chromium. AdGuard's earlier MV3 beta announcement listed further limits, including a maximum of 50 filters enabled at once. That post is older than the later changes above, so treat its numbers as dated and check the current extension.

## If you want to avoid the extension limits

AdGuard's own suggestion is a system-wide AdGuard app for Windows, Mac, Android or Linux, which it says filters traffic across browsers and other applications and does not depend on a browser's extension rules. We did not check whether such an app is free or paid.

## How it differs from uBlock Origin Lite

Both are MV3 blockers. AdGuard says it kept an engine of its own for hiding page elements, while the uBOL project describes Lite as entirely declarative. We found no independent test comparing how well they block, so we do not rank them. Our guide to [uBlock Origin Lite's modes and limits](https://frontbuffer.net/tech/ublock-origin-lite-filtering-modes-settings-and-limits/) covers the other side.

## What we could not confirm

- AdGuard's current rule and filter limits on Chrome and Edge, since its older numbers are dated.
- How closely the MV3 build matches the old MV2 extension on difficult sites. AdGuard's statements are its own.
- Whether Allow user scripts is needed in browsers other than Edge.

---
Sources:
- [The Manifest V2 era is over: Chrome removes AdGuard Ad Blocker MV2 from the Web Store, AdGuard](https://adguard.com/en/blog/adguard-adblocker-manifestv2-removal.html)
- [AdGuard Browser Extension v5.5.3.3 release notes, GitHub](https://github.com/AdguardTeam/AdguardBrowserExtension/releases/tag/v5.5.3.3)
- [Manifesting change: AdGuard Ad Blocker on MV3 moves from prototype to beta, AdGuard](https://adguard.com/en/blog/adguard-mv3-beta.html)
- [Frequently asked questions (FAQ), uBOL-home Wiki](https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-%28FAQ%29)

<!-- excerpt: AdGuard's browser extension now runs on Manifest V3 in Chrome and Edge. What AdGuard says changes, how custom filters work in Edge, and which numbers are dated. -->
<!-- tags: explainer, adguard, manifest-v3, chrome-extensions -->
