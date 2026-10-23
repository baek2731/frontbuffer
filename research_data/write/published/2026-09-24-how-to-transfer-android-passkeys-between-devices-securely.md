---
layout: single
title: 'How to transfer Android passkeys between devices securely'
date: 2026-09-24 14:42:00 +0000
last_modified_at: 2026-10-20 00:00:00 +0000
categories: [tech]
tags: ["guide", "android", "passkeys", "security"]
excerpt: 'Passkeys saved in Google Password Manager sync to a new Android phone through your Google account. Here is how to move them and what unlocks them there.'
header:
  image: https://images.frontbuffer.net/posts/how-to-transfer-android-passkeys-between-devices-securely/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

You do not export passkeys by hand when you switch Android phones. Passkeys saved in Google Password Manager are backed up and synced, and Google says they are always end-to-end encrypted. To use them on a new phone you sign in to your Google account and unlock them with either an existing device's screen lock or your Google Password Manager PIN.

*Checked October 20, 2026 against Google's Security Blog (2022), a Google blog post on passkey sync (September 2024) and Google Account Help. Google's pages may have changed since then, menu names vary by phone, and nothing here was tested on a device.*

---

## How passkey sync works

[Google's Security Blog](https://security.googleblog.com/2022/10/SecurityofPasskeysintheGooglePasswordManager.html) says a passkey in Google Password Manager is backed up with its private key uploaded only in encrypted form, using an encryption key that is accessible only on your own devices. Creating or using these passkeys requires a screen lock on the phone.

When you set up a new Android phone by transferring data from an older one, Google says the existing end-to-end encryption keys are securely transferred. To recover the key otherwise, you must enter the screen lock PIN, password or pattern of another existing device that had access to those keys. Restoring passkeys on a new device requires both being signed in to your Google account and an existing device's screen lock. Google says it does not know your screen lock.

Since September 2024, Google has also offered a [Google Password Manager PIN](https://blog.google/technology/safety-security/google-password-manager-passkeys-update-september-2024/). When you start using passkeys on a new device, you need either that PIN or the screen lock of your Android device. The PIN is six digits by default, or longer if you choose PIN options, and passkeys sync across Android, Windows, macOS and Linux computers.

---

## Move passkeys to a new Android phone

1. **Keep the old phone until you finish.** Recovery can require the old device's screen lock.
2. **Sign in to the same Google account** while setting up the new phone. If you use the setup option that transfers data from the old phone, Google says the encryption keys move with it.
3. **Set a screen lock on the new phone.** Google says passkeys in Google Password Manager require one.
4. **Enter the unlock factor when asked.** That is the old device's screen lock or your Google Password Manager PIN.
5. **Test a few sites** that use passkeys before you wipe or sell the old phone.

Passkeys saved in a third-party credential manager are separate. [Google Account Help](https://support.google.com/accounts/answer/13548313) notes that a passkey you removed from your Google account can still be offered if it remains in such a manager, and it points to that manager's own documentation for removing it. Check that documentation for how it moves passkeys.

---

## If recovery fails

Google's Security Blog says that signing in to an existing device and changing its screen lock resets the count of invalid recovery attempts, after which you can recover the keys on the new device by entering the existing device's new screen lock. It also says that after a screen lock is removed from a device, the old lock may still work for recovery on other devices for up to 64 days.

Google's pages we checked do not describe a way to recover passkeys when you have neither an existing device's screen lock nor the Google Password Manager PIN.

---

## Passkeys for your Google account

Passkeys you use to sign in to your Google account itself are listed at myaccount.google.com/signinoptions/passkeys. [Google's help page](https://support.google.com/accounts/answer/13548313) says that if you lose a device you can remove its passkey from your account there, and that passkeys need the phone's screen lock to be on. That page covers signing in to Google, not the passkeys you saved for other sites.

---

## Before you wipe the old phone

Once the new phone works, reset the old one with its own reset option. The menu name depends on the maker, so look for a factory reset in Settings. This guide does not cover the steps for each brand.

---

## Takeaway

Use the same Google account, set a screen lock, and have the old phone's screen lock or your Google Password Manager PIN ready when the new phone asks. Test a few passkeys before you wipe anything.

---

Sources:
- [Security of Passkeys in the Google Password Manager, Google Security Blog](https://security.googleblog.com/2022/10/SecurityofPasskeysintheGooglePasswordManager.html)
- [Sync passkeys securely across your devices, Google](https://blog.google/technology/safety-security/google-password-manager-passkeys-update-september-2024/)
- [Sign in with a passkey instead of a password, Google Account Help](https://support.google.com/accounts/answer/13548313)
