# How to transfer Android passkeys between devices securely

Android passkeys use the FIDO2 standard and tie private keys to the device's secure enclave. The private key never leaves the device in plaintext — migration works through Google Account cloud sync, not direct file transfer.

---

## How Passkey Migration Works

When you set up a passkey on an Android device signed into Google, Google Password Manager backs it up encrypted to your Google Account. The encryption uses your Google Account password and two-factor authentication as keys — Google cannot read the passkey data without them.

When you sign into your Google Account on a new Android device, passkeys sync automatically. No manual export step is needed. This is the primary migration path for most users.

---

## Upgrading to a New Android Device

1. Sign into your Google Account on the new device during setup.
2. When prompted, restore from your Google Account backup.
3. After setup completes, open Settings → Passwords → Passkeys to confirm your passkeys are present.
4. Test login on two or three services that use passkeys to verify they work.

If passkeys don't appear immediately, give sync a few minutes. You can manually trigger a sync via Settings → Google → Sync.

---

## Device-to-Device Transfer Tools

Android's built-in device transfer (via cable or Wi-Fi Direct) migrates apps, settings, and messages. For passkeys specifically, the transfer works by setting up your Google Account on the new device and triggering cloud sync — the tool doesn't directly copy passkey files. The outcome is the same: passkeys appear on the new device after sync completes.

---

## Lost or Factory Reset Device

If your old device is inaccessible, sign into your Google Account on a new device. Passkeys restore from the encrypted cloud backup after identity verification via two-factor authentication. This is why securing your Google Account with a strong password and 2FA is the most important step in passkey management.

---

## After Migration: Securing the Old Device

Once you've confirmed passkeys work on the new device:

1. Sign out of your Google Account on the old device.
2. Perform a factory reset: Settings → General Management → Reset → Factory data reset.

This removes all local passkey data. The cloud copy remains intact and accessible from any new device signed into the same account.

---

## Key Settings to Know

**View your passkeys:** Settings → Google → Autofill → Passwords → Passkeys

**Enable 2FA on your Google Account:** myaccount.google.com → Security → 2-Step Verification

**Check sync status:** Settings → Google → Sync now

---
Sources:
- [Google — Passkeys in Google Password Manager](https://support.google.com/accounts/answer/13548313)
- [FIDO Alliance — Passkey overview](https://fidoalliance.org/passkeys/)
- [Android — Google Account sync settings](https://support.google.com/android/answer/2819582)
