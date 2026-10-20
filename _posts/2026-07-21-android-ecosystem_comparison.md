---
layout: single
title: 'Samsung Secure Folder vs Google Files Safe Folder: Privacy Compared'
date: 2026-07-21 14:06:00 +0000
last_modified_at: 2026-10-20 00:00:00 +0000
categories: [tech]
tags: ["comparison", "android", "ecosystem"]
excerpt: 'Samsung Secure Folder is a Knox-protected space for apps and files. Google Files Safe Folder locks files behind a PIN or pattern. Here is how they differ.'
header:
  image: https://images.frontbuffer.net/posts/android-ecosystem_comparison/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

Samsung and Google both offer a "secure folder" on Android, but they protect different things. Samsung's Secure Folder is a protected space that can hold apps as well as files. Google's Safe Folder, inside the Files by Google app, holds files only. If you are deciding which to use, here is what each one does, and where each one falls short.

*Checked October 16, 2026 and updated October 20, 2026 against Samsung and press sources. Nothing here was tested on a phone, and menu names vary by version.*

---

## What Samsung Secure Folder does

[Samsung's support page](https://www.samsung.com/ca/support/mobile-devices/use-secure-folder-on-your-samsung-galaxy/) describes Secure Folder as a protected space for photos, files and apps. It sits behind its own passcode or biometric lock and is protected by Samsung Knox. [Samsung Knox's own page](https://www.samsungknox.com/en/solutions/secure-folder) lists adding apps from the Secure Folder, moving data from native apps with "Add to Secure Folder," and renaming or grouping the apps inside.

The part that surprises people is how apps work. [Samsung's UK page](https://www.samsung.com/uk/support/mobile-devices/what-is-the-secure-folder-and-how-do-i-use-it/) says that when you move an installed app into Secure Folder, a copy is created, and you can sign in to the copy with a different account. If you want the app only in Secure Folder, you have to uninstall the original from your Apps screen. So a Secure Folder app is a second copy, and the first copy stays visible until you remove it.

You can hide Secure Folder itself. Samsung says to turn off **Add Secure Folder to Apps screen**, or hide and unhide it from the Quick Settings panel. [Samsung's Singapore page](https://www.samsung.com/sg/support/mobile-devices/what-is-secure-folder-and-how-to-use-it-on-samsung-mobile-device/) adds that data and apps in Secure Folder cannot be moved to other devices by unapproved methods such as USB or Wi-Fi Direct, and that you should back up data elsewhere before saving it there.

Secure Folder is available on Samsung Galaxy phones only.

---

## What Google Files Safe Folder does

Safe Folder is a feature of the Files by Google app. [Android Central's launch report](https://www.androidcentral.com/files-google-gets-pin-protected-safe-folder-hide-your-personal-files) says it lets you protect documents, photos, videos and audio with a 4-digit PIN, works on Android 8.0 and newer, and locks as soon as you switch to another app. [MakeUseOf](https://www.makeuseof.com/protect-files-android-devices-files-by-google/) says you can choose either a PIN or a pattern, and describes an option to hide the Safe folder from the Browse tab.

[How-To Geek reports](https://www.howtogeek.com/684738/how-to-hide-files-with-googles-safe-folder-on-android/) that files moved into Safe Folder are not available to third-party apps. [XDA Developers](https://www.xda-developers.com/files-by-google-safe-folder-hide-private-files/) says Google encrypts the files, so they cannot be decrypted if you forget the PIN. Most of these reports date from the 2020 launch or from a 2022 guide, so check that the menu options still match your version.

Safe Folder stores files. It is not a place to run apps.

---

## How they compare

| | Samsung Secure Folder | Google Files Safe Folder |
|---|---|---|
| Protected by | Samsung Knox, with its own passcode or biometric lock | A PIN or pattern inside the Files app, with encrypted files |
| Holds apps | Yes, as copies you can sign in to separately | No |
| Holds files | Yes | Yes |
| Device requirement | Samsung Galaxy | Android 8.0 or newer with the Files app |
| Can the folder itself be hidden | Yes | Yes, through a hide option in the Browse tab, per MakeUseOf |
| If you forget the lock | Not covered in the pages checked | Files cannot be decrypted, per XDA |

---

## Does a Pixel have Secure Folder?

No, because Secure Folder is a Samsung Galaxy feature. On Android 15 and later, [Android's guide](https://www.android.com/articles/how-to-set-up-private-space/) describes Private Space, which hides apps and files behind a separate lock, and the Files by Google Safe Folder described above holds files only. Our comparison of [Android App Lock vs Samsung Secure Folder](https://frontbuffer.net/tech/android-1516-native-app-lock-vs-samsung-app-lock-privacy-fea/) covers Private Space in more detail.

---

## Which one to use

**Use Secure Folder** if you have a Galaxy phone and want a second login for an app, such as a separate messaging account, or a protected place for apps and files together. Remember to remove the original app if you want the app to exist only inside Secure Folder.

**Use Safe Folder** if you only need to hide specific files, you do not have a Samsung phone, or you want something with less setup.

The two are not competing products. If you have a Galaxy phone you can use both.

Neither tool is an app lock that protects an app where it sits on your home screen. Android's native App Lock is still in beta and Samsung has no equivalent yet. We cover that in [Android App Lock vs Samsung Secure Folder](https://frontbuffer.net/tech/android-1516-native-app-lock-vs-samsung-app-lock-privacy-fea/).

---

For a different part of the Android ecosystem, see [Google Photos Free Storage Policy: What Changed for Your Library](https://frontbuffer.net/tech/android-ecosystem_explainer/).

---

Sources:
1. [Use Secure Folder on your Samsung Galaxy, Samsung Canada Support](https://www.samsung.com/ca/support/mobile-devices/use-secure-folder-on-your-samsung-galaxy/)
2. [What is the Secure Folder and how do I use it, Samsung UK Support](https://www.samsung.com/uk/support/mobile-devices/what-is-the-secure-folder-and-how-do-i-use-it/)
3. [What is Secure Folder and how to use it on my phone, Samsung Singapore Support](https://www.samsung.com/sg/support/mobile-devices/what-is-secure-folder-and-how-to-use-it-on-samsung-mobile-device/)
4. [Secure Folder, Samsung Knox](https://www.samsungknox.com/en/solutions/secure-folder)
5. [Files by Google gets a PIN-protected Safe Folder, Android Central](https://www.androidcentral.com/files-google-gets-pin-protected-safe-folder-hide-your-personal-files)
6. [How to Protect Your Files Using Files by Google on Android, MakeUseOf](https://www.makeuseof.com/protect-files-android-devices-files-by-google/)
7. [How to Hide Files with Google's Safe Folder on Android, How-To Geek](https://www.howtogeek.com/684738/how-to-hide-files-with-googles-safe-folder-on-android/)
8. [Files by Google starts rolling out a Safe Folder, XDA Developers](https://www.xda-developers.com/files-by-google-safe-folder-hide-private-files/)
9. [How to set up private space, Android](https://www.android.com/articles/how-to-set-up-private-space/)
