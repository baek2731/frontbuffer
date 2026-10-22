# uBlock Origin Lite vs uBlock Origin: Which Should You Use?

The full uBlock Origin (uBO) and uBlock Origin Lite (uBOL) are two different extensions, not two versions of one. uBO needs Manifest V2, which Chrome has removed, so on Chrome you can only use Lite. Firefox still runs the full uBO, and Brave hosts it on its own servers. Which one you want depends mostly on the browser you use.

*Checked October 22, 2026 against the uBOL project's FAQ and Troubleshooting pages, Mozilla's add-on listing, Brave's blog and X post, Microsoft's Edge blog and Windows Central. Nothing here was tested in a browser.*

## By browser

| Browser | Full uBlock Origin | uBlock Origin Lite |
|---|---|---|
| Chrome | No longer works, because Manifest V2 support was removed | Available from the Chrome Web Store |
| Microsoft Edge | Being phased out. Microsoft says the consumer transition away from Manifest V2 starts in August 2026 and should finish by the end of 2026 | Lite works on Chromium browsers |
| Firefox | Yes. Mozilla lists it as Recommended, including on Firefox for Android | The Troubleshooting page covers Firefox |
| Brave | Yes. Brave hosts it and other Manifest V2 extensions on its own servers | Chromium-based, so Lite should also work |

For Chrome's removal timeline, see our [Manifest V3 explainer](https://frontbuffer.net/tech/what-is-chrome-manifest-v3-and-why-extensions-break/).

Brave says on its [blog](https://brave.com/blog/brave-shields-manifest-v3/) that it hosts uBlock Origin, uMatrix, AdGuard and NoScript for as long as it is able and the authors cooperate. Microsoft's [Edge blog](https://blogs.windows.com/msedgedev/2026/08/07/moving-the-microsoft-edge-extensions-ecosystem-forward-with-manifest-version-3/) describes the Edge schedule. Windows Central [reported](https://www.windowscentral.com/software-apps/mozilla-firefox-and-brave-keep-ublock-origin-alive-while-chrome-and-edge-block-the-adblocker) that Firefox and Brave keep uBO alive while Chrome and Edge drop it.

## What differs in how they filter

Per the uBOL project's [FAQ](https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-%28FAQ%29):

- **Dynamic filtering:** uBO has it, and Lite does not.
- **Cosmetic filtering:** uBO applies generic cosmetic filtering by default. Lite does not, unless you raise a site to Complete mode.
- **Filter lists:** Lite ships rulesets compiled when the extension is built, updated only when the extension updates. A June 2026 note says custom filters and external lists are now possible.
- **Hard sites:** Lite is generally less effective against sites that use anti-content-blocker measures, because many filters cannot be converted to declarative rules.
- **Startup reliability:** the maintainer says Lite filters reliably at browser launch because it is entirely declarative. He adds that this is not an issue for MV2-based uBO on Firefox.
- **Maintainer's advice:** he considers Lite too different from uBO to be an automatic replacement and says you must pick one based on what you expect from a blocker.

The FAQ declines to claim Lite is lighter on CPU or memory, saying only a proper benchmark could answer that.

## Which to use

- **You use Firefox:** the full uBO is the straightforward choice.
- **You use Brave:** the full uBO works through Brave's hosted Manifest V2 extensions, which you switch on under Settings, Extensions, Manifest v2 extensions. Brave also has built-in blocking.
- **You use Chrome and want to stay:** Lite is the Chrome option from the same developer. Expect it to behave differently on tricky sites.
- **You use Edge:** Lite is the longer-term option, since Microsoft is removing Manifest V2 support.
- **You need dynamic filtering:** that points to Firefox with the full uBO.

On Android, none of this applies to Chrome, which cannot run extensions. To see whether your own extensions still depend on Manifest V2, use our [guide to checking Manifest V2 extensions](https://frontbuffer.net/tech/how-to-check-if-chrome-extensions-use-manifest-v2/).

---
Sources:
- [Frequently asked questions (FAQ), uBOL-home Wiki](https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-%28FAQ%29)
- [Troubleshooting, uBOL-home Wiki](https://github.com/uBlockOrigin/uBOL-home/wiki/Troubleshooting)
- [uBlock Origin by Raymond Hill, Firefox Browser Add-ons](https://addons.mozilla.org/en-US/addon/ublock-origin/)
- [What Manifest V3 means for Brave Shields and the use of extensions in the Brave browser, Brave](https://brave.com/blog/brave-shields-manifest-v3/)
- [Moving the Microsoft Edge extensions ecosystem forward with Manifest Version 3, Microsoft Edge Blog](https://blogs.windows.com/msedgedev/2026/08/07/moving-the-microsoft-edge-extensions-ecosystem-forward-with-manifest-version-3/)
- [Mozilla Firefox and Brave keep uBlock Origin alive while Chrome and Edge block the adblocker, Windows Central](https://www.windowscentral.com/software-apps/mozilla-firefox-and-brave-keep-ublock-origin-alive-while-chrome-and-edge-block-the-adblocker)
