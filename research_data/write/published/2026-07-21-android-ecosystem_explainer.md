---
layout: single
title: 'Google Photos Free Storage Policy: What Changed for Your Library'
date: 2026-07-21 14:49:00 +0000
last_modified_at: 2026-10-16 00:00:00 +0000
categories: [tech]
tags: ["explainer", "android", "ecosystem"]
excerpt: 'Google ended free unlimited Google Photos backup on June 1, 2021. What still counts as free today, which Pixels keep the perk, and how to recover space.'
header:
  image: https://images.frontbuffer.net/posts/android-ecosystem_explainer/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

Google ended free unlimited photo backup on June 1, 2021, and that date is still the dividing line. [Google's help page](https://support.google.com/photos/answer/10100180?hl=en) says each Google Account comes with up to 15 GB of storage shared by Gmail, Google Drive and Google Photos, and that photos and videos backed up in High quality or Express quality before June 1, 2021 do not count against it. Everything backed up since then does count, whatever the quality setting, with one exception: older Pixel phones.

*Checked October 16, 2026 against Google's help pages and 9to5Google. Nothing here was tested in the app.*

---

## Which Pixels still get free backup

Google's page says that if you have a Pixel 5 or earlier, you get unlimited storage for photos and videos backed up from that device at no charge. Its [backup quality page](https://support.google.com/photos/answer/6220791?hl=en) adds the details:

| Phone | What Google says |
|---|---|
| Pixel 3a to Pixel 5 | Photos and videos backed up in Storage saver are unlimited and free |
| Older Pixels | Original quality was free up to cutoff dates of January 16, 2021 and January 31, 2022 on Google's page. Later backups use Storage saver at no charge |
| Original Pixel | One entry gives unlimited Original-quality storage with no Storage saver option. [Metadata Fixer](https://metadatafixer.com/learn/pixel-unlimited-google-photos-storage) says it applies to the original Pixel and Pixel XL, and that it still worked in early 2026 |
| Pixel 6 and later | Not covered. Google's wording stops at Pixel 5 |

Two cautions. Google describes the benefit as applying to photos and videos backed up from the Pixel itself. Some third-party guides suggest buying an old Pixel and uploading other photos through it, but Google's page does not describe that, and Google can change the policy, so this article does not recommend building a workflow on it. And "free" for the Pixel 3a to Pixel 5 means Storage saver quality, not original quality.

---

## Recover storage: shrink what you already uploaded

If you backed up photos in Original quality, you can convert them. On the Google Photos website, Google's help page says to go to Settings, then Manage storage, and under Recover storage choose **Convert existing photos & videos to Storage saver**. You can do this once a day.

The trade-off is resolution. Google says Storage saver resizes photos larger than 16 MP down to 16 MP and videos above 1080p down to 1080p. Google's page recommends Original quality for photos over 16 MP and videos over 1080p. Because Storage saver uploads now count against your storage too, the conversion saves space but does not make the photos free.

---

## What no longer works

**The T-Mobile unlimited plan.** [9to5Google reported](https://9to5google.com/2026/03/16/google-photos-unlimited-storage-subscription-ends/) that T-Mobile's "2TB + Unlimited Google Photos" Google One plan stopped taking new enrollment on September 30, 2025. T-Mobile's own notice, quoted there, says billing for existing subscribers moved to Google on March 31, 2026 and that the "Unlimited Photos & Videos" plans are no longer available after the move. A commenter on that article points out that Pixels 1 to 5 still have their device perk, which matches Google's page.

---

## What to do if your 15 GB is full

1. **Check what is using the space.** Google's help page says you can use its storage management tool to see how much space you have left and clean up.
2. **Convert existing originals** with Recover storage if you can accept 16 MP photos and 1080p video.
3. **On a Pixel 3a to Pixel 5, set backups to Storage saver,** since that is the quality Google lists as free.
4. **Delete duplicates and screenshots** you do not need.
5. **Consider a paid Google storage plan** if none of that is enough. Prices vary by country and plan name, and were not checked for this article.

---

For privacy-focused file storage on Android, see [Samsung Secure Folder vs Google Files Safe Folder](https://frontbuffer.net/tech/android-ecosystem_comparison/).

---

Sources:
1. [About your Google Photos activity & storage, Google Photos Help](https://support.google.com/photos/answer/10100180?hl=en)
2. [Choose the backup quality of your photos & videos, Google Photos Help](https://support.google.com/photos/answer/6220791?hl=en)
3. [The last remaining subscription for unlimited Google Photos storage is dead, 9to5Google](https://9to5google.com/2026/03/16/google-photos-unlimited-storage-subscription-ends/)
4. [Pixel 1 Unlimited Google Photos Storage, Metadata Fixer](https://metadatafixer.com/learn/pixel-unlimited-google-photos-storage)
