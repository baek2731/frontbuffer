---
layout: single
title: 'Samsung Health Not Syncing: Last Synced Date and Fixes'
date: 2026-10-19 14:18:00 +0000
categories: [tech]
tags: ["guide", "samsung", "health", "syncing", "fixes"]
excerpt: 'Samsung Health not syncing? Fix old "Last synced" dates, missing data, or app issues. Troubleshoot Samsung account, Health Connect, and watch sync'
author_profile: false
read_time: true
share: true
---

If Samsung Health shows an old "Last synced" date, or your data is missing on a new phone or in another app, first work out which sync is failing. Samsung Health has two separate ones: a sync with your Samsung account that backs data up and restores it on other devices, and a sync with Health Connect that shares data with other apps on the same phone. A watch also feeds the phone separately. The fixes differ for each, and most of the steps below come from Samsung support pages and from replies by Samsung staff on Samsung's community forums.

*Checked October 16, 2026. Samsung's menu labels have changed over time and differ by region, and nothing here was tested on a phone.*

## Which sync is broken

| Sync | What it does | Where to look |
|---|---|---|
| Samsung account sync | Backs up and restores data between devices through your Samsung account | Samsung's Canada page says Menu, Settings, then **Sync with Samsung account**. Samsung staff replies mention Settings, then **Accounts**, then **Auto Sync**. Other pages call it **Sync with Samsung Cloud** |
| Health Connect sync | Shares data between Samsung Health and other apps on the phone | Samsung Health, Settings, **Health Connect**, **Data and access**, per [Samsung Developers](https://developer.samsung.com/health/blog/en/accessing-samsung-health-data-through-health-connect) |
| Watch to phone | Moves watch data to the phone app | Check the network and app updates, per [Samsung's US troubleshooting page](https://www.samsung.com/us/support/troubleshooting/TSG01003270). If the watch was set up without a phone, its recent activity is stored only on the watch |

## Fix the Samsung account sync

Work through these in order.

1. **Check the switch and press Sync now.** [Samsung's Canada support page](https://www.samsung.com/ca/support/mobile-devices/galaxy-phone-sync-your-data-in-samsung-health/), updated November 2024, says syncing backs up and restores your data through your Samsung account. It describes turning the sync on, an optional **Sync only on Wi-Fi** switch, and a **Sync now** option in the menu. If the Wi-Fi-only switch is on, sync waits for Wi-Fi.
2. **Turn sync off, restart the phone, turn it back on.** A Samsung community moderator gave this advice to a user whose [Last synced date showed December 31, 1969](https://us.community.samsung.com/t5/Samsung-Apps-and-Services/samsung-health-app-stays-synced-at-1-jan1970/td-p/2738985).
3. **Clear the app's cache.** Samsung staff on Samsung Members suggest Settings, Apps, Samsung Health, Force stop, then Storage and Clear cache. Do not choose Clear data. See the warning below.
4. **Update the app and the phone.** The same [Samsung Members reply](https://r2.community.samsung.com/t5/Galaxy-S/Now-Bar-Samsung-Heath-Issues/m-p/23069943) lists a software update and the latest Samsung Health version.
5. **Check the privacy consent after an update.** One user on Samsung's EU community reported that after Samsung Health 7.00.0.107, sync failed with "Couldn't sync, go to settings" and the sync page kept loading. The fix was turning **Consent to the processing of health and wellness data** back on under [Settings, Privacy](https://eu.community.samsung.com/t5/health-club/samsung-health-not-syncing/td-p/14958220). That is one user's report, not a Samsung statement.
6. **Send an error report if it still fails.** Samsung staff ask for a screenshot of the error and the app's logs, available under Settings, Error reports.

## Fix the Health Connect sync

- **Open Settings, Health Connect, Data and access** in Samsung Health and confirm the data types you want are turned on.
- **Check Sync with Samsung Cloud.** Samsung Developers lists it as part of the sync settings. One developer on Samsung's US community reported that Samsung Health [was not writing to Health Connect until Sync with Samsung Cloud was turned on](https://us.community.samsung.com/t5/Samsung-Apps-and-Services/Samsung-Health-Not-Writing-to-Health-Connect/td-p/3358964), again a single user's report.
- **A newly connected app sees only about 30 days of history by default,** according to [Android's documentation](https://developer.android.com/health-and-fitness/guides/health-connect/develop/read-data). That is how Health Connect works, not a sync failure.

## Do not reset the app to fix sync

One user on Samsung's US community reset Samsung Health after sync stopped, which cleared their statistics. The app then showed "No synced data," and the data came back only after it resynced, according to the [thread](https://us.community.samsung.com/t5/Galaxy-S21/Samsung-Health-not-syncing-for-days/td-p/3367951). The accepted answer in that thread says a resync after a reset may take time, and that you should be signed in with the correct Samsung account and have a stable connection.

Because a reset can erase local data, download a copy first. Our guide on [backing up Samsung Health data](https://frontbuffer.net/tech/how-to-backup-samsung-health-data-before-account-deletion/) covers the download and the Samsung Cloud backup. For how Samsung Health and Health Connect fit together, see [Samsung Health vs Google Health Connect](https://frontbuffer.net/tech/samsung-health-vs-google-health-connect-feature-comparison/).

## If nothing works

Contact Samsung Support with the error message and the log file from Settings, Error reports. Samsung's pages checked for this article do not list a fix beyond these steps.

---
Sources:
- [Sync your data in Samsung Health on your Galaxy phone, Samsung Canada Support](https://www.samsung.com/ca/support/mobile-devices/galaxy-phone-sync-your-data-in-samsung-health/)
- [Samsung Health data does not sync, Samsung US Support](https://www.samsung.com/us/support/troubleshooting/TSG01003270)
- [Accessing Samsung Health Data through Health Connect, Samsung Developers](https://developer.samsung.com/health/blog/en/accessing-samsung-health-data-through-health-connect)
- [Samsung Health Last Synced Date, Samsung Community](https://us.community.samsung.com/t5/Samsung-Apps-and-Services/samsung-health-app-stays-synced-at-1-jan1970/td-p/2738985)
- [Now Bar Samsung Heath Issues, Samsung Members](https://r2.community.samsung.com/t5/Galaxy-S/Now-Bar-Samsung-Heath-Issues/m-p/23069943)
- [Samsung Health not syncing, Samsung Community (EU)](https://eu.community.samsung.com/t5/health-club/samsung-health-not-syncing/td-p/14958220)
- [Samsung Health Not Writing to Health Connect, Samsung Community](https://us.community.samsung.com/t5/Samsung-Apps-and-Services/Samsung-Health-Not-Writing-to-Health-Connect/td-p/3358964)
- [Samsung Health not syncing for days, Samsung Community](https://us.community.samsung.com/t5/Galaxy-S21/Samsung-Health-not-syncing-for-days/td-p/3367951)
- [Read raw data, Android Developers](https://developer.android.com/health-and-fitness/guides/health-connect/develop/read-data)
