---
layout: single
title: 'How to Transfer Samsung Health Data to a New Phone Without Loss'
date: 2026-07-22 14:03:00 +0000
last_modified_at: 2026-10-20 00:00:00 +0000
categories: [tech]
tags: ["guide", "android", "ecosystem"]
excerpt: 'Samsung Health data transfers automatically via Samsung Cloud, but only if sync was enabled before you switched. Here is how to move it to a new phone.'
header:
  image: https://images.frontbuffer.net/posts/android-ecosystem_guide/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

To move Samsung Health to a new phone, sync your data to your Samsung account on the old phone, then sign in with the same account on the new one. Samsung's support page says syncing backs up and restores your Samsung Health data through your Samsung account, so you can get it on another device. A [Samsung Members reply](https://r1.community.samsung.com/t5/samsung-health/restore-personal-health-data/td-p/37436826) says that this sync is the only supported way to restore health data on a new device, and that your data syncs automatically once you sign in if sync was enabled.

*Checked October 16, 2026 against Samsung support pages and community replies. Menu labels differ by version and region, and nothing here was tested on a phone.*

---

## How to transfer Samsung Health data to a new phone

1. **On the old phone, open Samsung Health and find the sync setting.** [Samsung's Canada page](https://www.samsung.com/ca/support/mobile-devices/galaxy-phone-sync-your-data-in-samsung-health/), updated November 2024, calls it **Sync with Samsung account**. [Samsung's US page](https://www.samsung.com/us/support/answer/ANS10001399) calls it **Sync with Samsung Cloud**. Same feature, different label.
2. **Turn it on and tap Sync now.** The Canada page also describes a **Sync only on Wi-Fi** switch, which you can leave off if you want to use mobile data.
3. **Make sure the sync finished** before you set up the new phone. For a second copy of your data as a precaution, see our guide to [backing up Samsung Health data](https://frontbuffer.net/tech/how-to-backup-samsung-health-data-before-account-deletion/). If the Last synced date is old or the sync fails, fix that first with our guide to [Samsung Health not syncing](https://frontbuffer.net/tech/samsung-health-not-syncing-last-synced-date-and-fixes/).
4. **On the new phone, install or open Samsung Health and sign in with the same Samsung account.** A different account will not have your data.
5. **Wait for the data to appear,** then check your activity history to confirm.

---

## How to restore Samsung Health data

Samsung also describes a manual route. [Samsung's Singapore support page](https://www.samsung.com/sg/support/apps-services/how-to-restore-or-backup-samsung-health-data/) says that you need a network connection and a Samsung account with your data synced, and that you can choose **Back up data** or **Restore data** under Samsung Cloud in the app's settings. That page was last updated in 2022, so labels may have moved.

**Exports do not restore data.** Samsung's download option saves a copy of your data for your records. The Samsung pages checked do not describe importing the downloaded files back into Samsung Health. The only supported restore route per the Samsung Members reply is the sync above.

---

## If you are moving to a non-Samsung Android phone

You can still use Samsung Health. [Samsung's 2015 announcement](https://news.samsung.com/global/samsung-introduces-the-next-generation-of-s-health-expands-compatibility-to-other-android-devices) said the app supports non-Samsung Android devices, with the note that tablets and some devices may not be supported. That announcement is old, so confirm current support for your phone. One user on Samsung's community forum who moved [from a Nexus 5 to a Pixel](https://eu.community.samsung.com/t5/mobile-apps-services/samsung-health-app-can-t-restore-data-to-new-phone/td-p/250676) reinstalled Samsung Health and signed in with their Samsung account. Treat that as one user's report, not a guarantee.

Health Connect is separate. It shares data between apps on a phone and is not a way to move your Samsung Health history. See our [Samsung Health and Health Connect comparison](https://frontbuffer.net/tech/samsung-health-vs-google-health-connect-feature-comparison/).

---

## If data is missing after the switch

- **Check the account.** Make sure you used the same Samsung account on both phones.
- **Check that the old phone had synced.** If it never finished, see [Samsung Health not syncing](https://frontbuffer.net/tech/samsung-health-not-syncing-last-synced-date-and-fixes/). Samsung's community thread on a [transfer between two Galaxy phones](https://eu.community.samsung.com/t5/mobile-apps-services/samsung-health-data-transfer/td-p/14124140) shows a user missing only daily step counts after syncing. A reply there suggests waiting at least three days for everything to sync. The user later restored the missing data by backing up the app with Smart Switch on the old phone and restoring it on the new one. Both are single community reports, not Samsung statements.
- **If sync was never on,** the data was not backed up to your account. The Samsung Members reply makes enabling sync before the switch the condition for the restore.

---

If you plan to delete your Samsung account after switching, download a copy first, as covered in [How to Backup Samsung Health Data Before Account Deletion](https://frontbuffer.net/tech/how-to-backup-samsung-health-data-before-account-deletion/).

---

Sources:
1. [Sync your data in Samsung Health on your Galaxy phone, Samsung Canada Support](https://www.samsung.com/ca/support/mobile-devices/galaxy-phone-sync-your-data-in-samsung-health/)
2. [Sync your data in Samsung Health, Samsung US Support](https://www.samsung.com/us/support/answer/ANS10001399)
3. [How to Restore or Backup Samsung Health Data, Samsung Singapore Support](https://www.samsung.com/sg/support/apps-services/how-to-restore-or-backup-samsung-health-data/)
4. [Restore personal health data, Samsung Members](https://r1.community.samsung.com/t5/samsung-health/restore-personal-health-data/td-p/37436826)
5. [Samsung Introduces the Next Generation of S Health, Samsung Newsroom](https://news.samsung.com/global/samsung-introduces-the-next-generation-of-s-health-expands-compatibility-to-other-android-devices)
6. [Samsung Health app - can't restore data to new phone, Samsung Community](https://eu.community.samsung.com/t5/mobile-apps-services/samsung-health-app-can-t-restore-data-to-new-phone/td-p/250676)
7. [Samsung health data transfer, Samsung Community](https://eu.community.samsung.com/t5/mobile-apps-services/samsung-health-data-transfer/td-p/14124140)
