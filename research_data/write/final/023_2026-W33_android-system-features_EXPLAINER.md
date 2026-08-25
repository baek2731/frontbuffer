---
layout: single
title: 'Google Messages Long-Press Menu Redesign: What Changed and How to Use It'
date: 2026-08-27 14:00:00 +0000
categories: [tech]
tags: ["explainer", "android", "system", "features"]
excerpt: 'Google Messages replaced its top toolbar with a floating long-press menu in its August 2026 beta rollout. The change adds precise text copying and one-handed access to Reply and Edit.'
header:
  image: https://images.frontbuffer.net/posts/android-system-features_explainer/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

Google Messages replaced its top toolbar with a floating long-press menu in its August 2026 beta rollout. The redesign moves common actions — Reply, Forward, Copy, Star, Delete — into a vertical list that appears closer to the thumb, reducing the distance your hand needs to travel for one-handed use.

---

## What the Old Menu Did and Why It Changed

The previous long-press menu appeared as a toolbar at the top of the screen. For users holding their phone with one hand, reaching the top of the display to tap Copy or Reply required either repositioning the phone or using two hands. As screen sizes increased, this became more noticeable.

The floating menu addresses this by anchoring to the message being long-pressed rather than the top of the screen. The menu position varies based on where the message sits in the conversation — messages near the bottom of the screen produce a menu that appears above them, keeping it within thumb reach.

---

## New Features in the Redesigned Menu

**Precise text copying.** A second long-press on a message opens a text selection mode, letting you copy a specific phrase rather than the entire message. Previously, long-pressing copied the full message with no partial selection option.

**Direct Edit access.** For RCS messages sent within the 15-minute editing window, Edit appears directly in the floating menu. The previous toolbar required tapping a three-dot overflow menu to find it.

**Haptic feedback.** The redesigned menu includes haptic feedback when it opens, giving tactile confirmation without looking at the screen.

---

## Message Editing: What to Know

Google Messages allows editing sent RCS messages within 15 minutes of sending. After editing, the message displays an "Edited" label visible to the recipient. Edit history is not currently shown to recipients — only the final version of the message appears.

For conversations between Android and iPhone users using RCS (available since iOS 18), editing works within the RCS framework when both parties have RCS enabled. If the conversation falls back to SMS/MMS — which happens when RCS is unavailable on either end — editing is not possible.

---

## Privacy Controls for Lock Screen Notifications

A recurring user concern is message content appearing on the lock screen. Google Messages follows Android's notification system for this:

**Settings → Notifications → Lock screen → Notifications on lock screen**

Options are: Show all notification content, Hide sensitive notification content, or Don't show notifications. "Hide sensitive notification content" shows that a message arrived but not its text.

Some users on Android 15 and 16 have reported that default lock screen settings don't consistently apply after system updates. If content appears despite your settings, re-toggle the option off and back on to force it to apply.

---

## Storage Management in Google Messages

Google Messages stores photos and videos received in conversations locally. There's no automatic deletion for old threads, but you can manage storage manually:

- **Free up space:** Tap your profile photo → Manage storage → Storage usage shows which conversations use the most space
- **Delete media from a thread:** Open the conversation → tap the contact name → View media → select items → Delete
- **Auto-delete OTP messages:** Settings → Message organization → Auto-delete OTPs — removes one-time password messages after 24 hours

---

## How to Get the Redesigned Menu

The floating long-press menu is rolling out through the Google Messages beta program as of August 2026. To access it:

1. Open Google Play Store → search Google Messages
2. Scroll to "Join the beta" and tap **Join**
3. Update Google Messages after joining

Beta features roll out gradually — joining the beta doesn't guarantee immediate access, but most beta users receive the update within a few days of joining.

---
Sources:
- [9to5Google — Google Messages long-press menu redesign](https://9to5google.com/2026/08/google-messages-long-press-menu-redesign/)
- [Android Authority — Google Messages one-handed use](https://www.androidauthority.com/google-messages-long-press-menu-3400000/)
- [Google — Change Messages notifications & settings](https://support.google.com/messages/answer/7189714)
