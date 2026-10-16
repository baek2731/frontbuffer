---
layout: single
title: 'Android App Lock vs Samsung Secure Folder: What Exists Today'
date: 2026-08-28 14:55:00 +0000
last_modified_at: 2026-10-16 00:00:00 +0000
categories: [tech]
tags: ["comparison", "android", "privacy", "samsung"]
excerpt: 'Android''s native App Lock is still in beta and Samsung has none yet. Private Space and Secure Folder are the options today. What each does, and what is coming.'
header:
  image: https://images.frontbuffer.net/posts/android-1516-native-app-lock-vs-samsung-app-lock-privacy-fea/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

If you want to lock a single app behind your fingerprint or PIN, Android does not have a finished way to do it yet. Android 15 added Private Space, which is a different tool, and Google's native App Lock is still in beta testing. Samsung phones have Secure Folder, and a built-in App Lock has only appeared in a leak. This article explains what each option does today and what is coming.

*Checked October 16, 2026 against press reports. Nothing here was tested on a phone, and the App Lock details come from beta builds and leaks that can change.*

---

## Where things stand

| | Pixel and other Android phones | Samsung Galaxy phones |
|---|---|---|
| Available now | Private Space (Android 15) | Secure Folder |
| Per-app lock | App Lock, in testing in Android 17 QPR2 Beta 3 | Not available. A leaked One UI 9.5 build shows one |
| Expected | Final Android 17 QPR2 is likely in December | One UI 9.5 is expected with the Galaxy S27 series next year |

---

## Private Space: a separate locked area

Google introduced Private Space with Android 15. [Android Police notes](https://www.androidpolice.com/android-17-native-app-lock-private-space/) it is designed as a segregated space for your data and apps, not specifically as an app locker. [BGR describes](https://www.bgr.com/2215112/google-pixel-adding-app-lock-feature/) it as a second locked interface inside the phone. You cannot tap an app on the home screen and unlock just that app. You open Private Space first, enter your password, and then open the app. The version of an app you install in Private Space is separate from the normal one, so to keep an app out of reach you have to delete it outside Private Space.

[Android Authority](https://www.androidauthority.com/android-17-app-lock-rumor-3623814/) adds that apps inside Private Space cannot be placed on the home screen, and that the container itself lacks a shortcut.

---

## Android's native App Lock: in testing

Android Authority found evidence of an App Lock feature in Android Canary 2512 in December 2025. [Forbes quotes](https://www.forbes.com/sites/zakdoffman/2025/12/11/googles-new-android-update-locks-apps-on-pixel-and-samsung-phones/) its finding as a new API that allows the default launcher to lock apps, removing the need for third-party app lockers.

The feature is now in testing. [Yahoo Tech, citing 9to5Google,](https://tech.yahoo.com/phones/articles/app-lock-finally-coming-android-112804962.html) reports it in Android 17 QPR2 Beta 3 on Pixel phones. You long-press an app icon and choose the option at the end of the list, and after setup the phone's unlock method is required each time you open the selected app. The final Android 17 QPR2 is not likely before December.

BGR, citing strings found by Android Authority, says the feature works more like the App Lock on OnePlus phones than like Secure Folder. Each app is locked independently instead of being placed in an isolated space. Beta features can change or be dropped before release.

---

## Samsung Secure Folder: what Galaxy phones have

[Android Authority says](https://www.androidauthority.com/samsung-one-ui-9-5-app-lock-leak-3698657/) Samsung phones do not have a native app lock. You use Secure Folder, which hides an app by adding it to a protected folder that needs a PIN, password or biometric scan. [Digital Trends describes](https://www.digitaltrends.com/phones/galaxy-phones-may-finally-get-a-basic-privacy-feature-samsung-missed/) Secure Folder as a separate protected environment for apps, files, photos and accounts behind another authentication layer.

There is a catch. Android Authority points out that adding an app to Secure Folder creates a cloned app, and the original is still in the app drawer, open without a PIN or biometric scan. Samsung users who want only the protected copy have to deal with the original separately.

---

## Samsung's App Lock leak

A tipster found an App Lock feature in an unreleased One UI 9.5 build on a Galaxy S26, per Android Authority and Digital Trends. The lock icon appears when you press and hold an app icon in the app drawer, a locked app opens with biometrics or the screen lock, and Digital Trends adds that the feature also hides the app's notifications, widgets and shortcuts.

This is a leak, not an announcement. [Android Headlines](https://www.androidheadlines.com/2026/08/samsung-is-finally-adding-app-lock-soon-heres-how-it-works.html) says the feature was expected with One UI 9, which did not happen, and that One UI 9.5 is expected with the Galaxy S27 series in the first quarter of next year.

---

## Which to use today

- **You have a Pixel and want to hide a few apps:** Private Space works now, but it is an isolated area, not a per-app lock.
- **You have a Galaxy phone:** Secure Folder is the built-in option. Plan for the cloned-app behavior described above.
- **You want a simple per-app lock without either of those:** third-party app lockers are the only option today. [Android Authority](https://www.androidauthority.com/android-17-app-lock-rumor-3623814/) notes that Android lacks a native way to do this apart from Private Space, which is why users rely on third-party tools.
- **You can wait:** Android's App Lock may arrive with the final Android 17 QPR2 in December, and a Samsung version looks more likely next year.

---
Sources:
- [Android 17 may finally add the native App Lock feature Pixel users have been waiting for, Android Authority](https://www.androidauthority.com/android-17-app-lock-rumor-3623814/)
- [Android's native App Lock feature may arrive next year, Android Police](https://www.androidpolice.com/android-17-native-app-lock-private-space/)
- [App Lock Is Finally Coming to Android: Pixel Up First, Samsung May Be Next, Yahoo Tech](https://tech.yahoo.com/phones/articles/app-lock-finally-coming-android-112804962.html)
- [Google Pixel May Finally Be Adding A Feature Every Other Android Phone Has, BGR](https://www.bgr.com/2215112/google-pixel-adding-app-lock-feature/)
- [Google's New Android Update Locks Apps On Pixel And Samsung Phones, Forbes](https://www.forbes.com/sites/zakdoffman/2025/12/11/googles-new-android-update-locks-apps-on-pixel-and-samsung-phones/)
- [Samsung phones could finally get proper app lock with One UI 9.5, Android Authority](https://www.androidauthority.com/samsung-one-ui-9-5-app-lock-leak-3698657/)
- [Galaxy phones may finally get a basic privacy feature Samsung missed, Digital Trends](https://www.digitaltrends.com/phones/galaxy-phones-may-finally-get-a-basic-privacy-feature-samsung-missed/)
- [Samsung Is Finally Adding App Lock, Soon, Android Headlines](https://www.androidheadlines.com/2026/08/samsung-is-finally-adding-app-lock-soon-heres-how-it-works.html)
