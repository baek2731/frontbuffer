---
layout: single
title: 'Google Messages Long-Press Menu: What Changed and How to Use It'
date: 2026-09-07 14:10:00 +0000
last_modified_at: 2026-10-20 00:00:00 +0000
categories: [tech]
tags: ["explainer", "android", "google-messages", "features"]
excerpt: 'Google Messages now opens a floating menu when you long-press a message, and lets you copy just part of the text. What it holds, how to use it, and who gets it.'
header:
  image: https://images.frontbuffer.net/posts/android-system-features/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

Long-pressing a message in Google Messages no longer opens a toolbar at the top of the screen. It opens a floating menu with the actions listed in a vertical list, and a second long-press on the text lets you copy only part of a message. Google says the redesign has officially launched, so it is no longer a beta-only feature.

*Checked October 16, 2026 and updated October 20, 2026 against press reports and Google's help page. Nothing here was tested in the app.*

---

## What the old menu did, and what replaced it

Before the redesign, long-pressing a message showed a toolbar at the top of the screen with three actions on the right and everything else in a three-dot overflow menu, [9to5Google reports](https://9to5google.com/2026/08/06/google-messages-menu-redesign/). That was awkward on large phones, which the redesign targets with one-handed use in mind.

The new menu blurs the background and shows a vertical list. For a text message the list holds Reply, Forward, Copy, Star, Delete, Select more and Info. For photos it adds Remix and Save, according to [9to5Google's first report in January](https://9to5google.com/2026/01/07/google-messages-long-press-menu/). The emoji row above the message is unchanged. If there is not enough room for the list, the selected message moves higher on the screen with a bouncy animation, and 9to5Google also noted haptic feedback when the menu opens.

---

## How to copy part of a message

Previously Copy took the whole message. After the redesign, 9to5Google describes this sequence:

1. Long-press a message to open the new menu.
2. Long-press again directly on the text in that message.
3. Drag the selection handles to highlight the part you want.
4. In the box that appears, choose Copy, Translate or Select All.

---

## Editing a sent message

Google's [help page for updating a sent message](https://support.google.com/messages/answer/14929292?hl=en) says you can edit an RCS, SMS or MMS message after sending it, in the app only, and that the ability expires after 15 minutes. An "Edited" label appears above the message for both the sender and the recipient. On SMS, the recipient gets another message starting with an asterisk. Editing also works in one-on-one chats with iPhone users who have RCS turned on.

The help page still tells you to touch and hold a sent message and tap Edit at the top of the screen. One outlet, [The Tech Basket](https://www.thetechbasket.com/google-messages-update/), says Google's announcement lists editing a recently sent message in the new menu. Which one you see may depend on whether the redesign has reached your app.

---

## Reply gesture changes: swipe right to reply, swipe left for timestamps

Google changed two gestures in the same rollout, [9to5Google reports](https://9to5google.com/2026/09/25/google-messages-timestamps-reply/). Before, tapping a bubble showed its sent time, read receipts and the RCS lock, and swiping left started a direct reply. Now:

- **Swipe left anywhere in a conversation** to show the timestamps, and the RCS encryption status, for the whole thread at once.
- **Swipe right on a specific bubble** to reply to that message. 9to5Google says this takes some precision, because you have to start the swipe on the bubble.
- **Tap a message** to see its read receipts, per 9to5Google. [Android Authority](https://androidauthority.com/google-messages-swipe-3715719) says a tap now shows delivery status. After a tap, Messages briefly lets the timestamps peek out as a hint about the new behavior.

[gHacks](https://www.ghacks.net/2026/09/26/google-messages-adds-a-floating-long-press-menu-and-new-swipe-gestures-for-timestamps-and-replies/) and [Android Central](https://www.androidcentral.com/apps-software/google-messages-gets-a-major-gesture-and-menu-refresh) describe the same two swipes.

---

## When you get it

The timeline from the reports:

- **January 2026:** testing began with a beta build, per 9to5Google.
- **August 6:** 9to5Google saw the redesign expand in the beta, in build 20260731_00_RC00, through a server-side update.
- **September:** users reported it on the stable app. [Android Headlines](https://www.androidheadlines.com/2026/09/google-messages-finally-rolls-out-a-handy-new-long-press-menu.html) cites stable build v20260903_04.
- **September 25:** 9to5Google and Android Authority reported the swipe gestures rolling out widely. 9to5Google noted that the older two-circle read receipt design was the one appearing most often.
- **September 30:** [9to5Google reports](https://9to5google.com/2026/10/01/google-messages-long-press-menu-wide/) that Google announced the redesign has officially launched.

Because the rollout is server-side, updating Google Messages from the Play Store may not show the new menu right away. Since the feature has reached the stable app, joining the beta is not needed for it. If you do not see the menu yet, check back after updating the app.

---
Sources:
- [Google Messages rolls out new long-press menu with partial copying, 9to5Google](https://9to5google.com/2026/10/01/google-messages-long-press-menu-wide/)
- [Google Messages rolling out long-press menu redesign with precise copying, 9to5Google](https://9to5google.com/2026/08/06/google-messages-menu-redesign/)
- [Google Messages getting new long-press menu for texts, images, 9to5Google](https://9to5google.com/2026/01/07/google-messages-long-press-menu/)
- [Google Messages rolls out new swipe for timestamps and reply gesture, 9to5Google](https://9to5google.com/2026/09/25/google-messages-timestamps-reply/)
- [Where's my timestamp? Google Messages is updating its UI, Android Authority](https://androidauthority.com/google-messages-swipe-3715719)
- [Update a sent message, Google Messages Help](https://support.google.com/messages/answer/14929292?hl=en)
- [Google Messages Adds a Floating Long-Press Menu and New Swipe Gestures, gHacks](https://www.ghacks.net/2026/09/26/google-messages-adds-a-floating-long-press-menu-and-new-swipe-gestures-for-timestamps-and-replies/)
- [Google Messages gets a major gesture and menu refresh, Android Central](https://www.androidcentral.com/apps-software/google-messages-gets-a-major-gesture-and-menu-refresh)
- [Google Messages Finally Rolls Out a Handy New Long-Press Menu, Android Headlines](https://www.androidheadlines.com/2026/09/google-messages-finally-rolls-out-a-handy-new-long-press-menu.html)
- [Google Messages Update: Partial Copy, New Menu and Games, The Tech Basket](https://www.thetechbasket.com/google-messages-update/)
