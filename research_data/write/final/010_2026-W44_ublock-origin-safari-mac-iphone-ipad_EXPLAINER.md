# Does uBlock Origin Work on Safari? Mac, iPhone and iPad

Not the full uBlock Origin. Reports say the full extension is no longer available for current Safari and has never run on iPhone or iPad, but uBlock Origin Lite is available from the App Store for Mac, iPhone and iPad. Lite is a different, more limited extension, and it has to be switched on in Safari's settings after you install it.

*Checked October 28, 2026 against the [App Store listing](https://apps.apple.com/us/app/ublock-origin-lite/id6745342698) (we confirmed the link but did not read its requirements), gHacks, Yahoo Tech, GIGAZINE, Setapp and the uBOL project's Troubleshooting page. Version requirements come from reports. Nothing here was tested on an Apple device.*

## Why the full version is not on Safari

Yahoo Tech reports that a version of the regular uBlock Origin once existed for Safari but was discontinued several years ago, when Apple moved from its older extension API to a more restrictive model called Safari App Extensions. It adds that the full extension was never available for iPhone or iPad. Setapp's guide gives a similar account and says the original extension has been incompatible with Safari since version 13.

## What you can install instead

[gHacks reported on August 5, 2025](https://www.ghacks.net/2025/08/05/ublock-origin-lite-for-safari-released-for-ios-ipados-and-macos/) that uBlock Origin Lite had arrived on the App Store for iOS, iPadOS and macOS. At launch it listed iOS 18.0, iPadOS 18.0, macOS 15.0 and visionOS 2.0 as minimums, and gHacks said Safari 18.6 or newer was needed. A later Setapp guide says the listing requires macOS 13.5 and iOS 18.5 or newer. The two reports differ, so read the requirements on the App Store listing for your own device before you install.

Lite is entirely declarative, which is how the uBOL project describes it, and its filtering modes are the same ones described in our guide to [uBlock Origin Lite's modes, settings and limits](https://frontbuffer.net/tech/ublock-origin-lite-filtering-modes-settings-and-limits/). gHacks lists the levels in Safari as No filtering, Basic, Optimal (the default) and Complete.

## Turn it on

1. Install uBlock Origin Lite from the App Store. When you open the app, GIGAZINE says it shows only a message that you can enable the extension in the Settings app.
2. On an iPhone or iPad, GIGAZINE describes opening **Settings**, then **Apps**, then **Safari**, then **Extensions**, and turning on uBlock Origin Lite. gHacks and Mac Observer describe **Settings, Safari, Extensions** on earlier iOS versions, so the path depends on your iOS version.
3. Allow the website access the extension asks for, then open a web page in Safari and use the extensions button to pick a filtering mode.
4. On a Mac, use the same place where Safari lists its extensions.

## If nothing is blocked

- The uBOL Troubleshooting page says to make sure Safari is allowed to use content blockers.
- Open a page in a new tab after changing a setting.
- GIGAZINE reports that its writer could not see the extension in Settings until turning off **Screen Time, Content & Privacy Restrictions**, which GIGAZINE says it found in an answer on Apple's support community. We did not verify that step.
- Run one content blocker at a time. The uBOL FAQ says not to use another content blocker alongside Lite.

## What we could not confirm

- The current minimum macOS, iOS and Safari versions, since reports disagree.
- Whether Lite behaves the same on Safari as in Chrome, Edge and Firefox. We found no side-by-side test.
- How well it blocks ads on a given site. gHacks reports that its writer saw ads blocked on YouTube in testing on iOS 18.6 and macOS 26.0 beta, which is one person's result on two versions.

---
Sources:
- [uBlock Origin Lite, App Store](https://apps.apple.com/us/app/ublock-origin-lite/id6745342698)
- [uBlock Origin Lite for Safari released for iOS, iPadOS, and macOS, gHacks](https://www.ghacks.net/2025/08/05/ublock-origin-lite-for-safari-released-for-ios-ipados-and-macos/)
- [uBlock Origin Lite Is Finally Available on Safari, Yahoo Tech](https://tech.yahoo.com/apps/articles/ublock-origin-lite-finally-available-225058235.html)
- [Free ad blocker uBlock Origin Lite finally available for Safari, GIGAZINE](https://gigazine.net/gsc_news/en/20250806-ublock-origin-lite/)
- [uBlock Origin for Safari: Best alternatives in 2026, Setapp](https://setapp.com/how-to/ublock-origin-for-safari)
- [Troubleshooting, uBOL-home Wiki](https://github.com/uBlockOrigin/uBOL-home/wiki/Troubleshooting)
- [uBlock Origin for iOS: Quick setup guide, Mac Observer](https://www.macobserver.com/tips/how-to/ublock-origin-ios/)

<!-- excerpt: The full uBlock Origin is not available for current Safari. uBlock Origin Lite is, on Mac, iPhone and iPad. How to turn it on, and where reports disagree. -->
<!-- tags: explainer, ublock-origin-lite, safari, ios -->
