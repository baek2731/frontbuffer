# How to Backup Samsung Health Data Before Switching Phones or Factory Reset

When upgrading to a new Samsung Galaxy device or performing a factory reset, Samsung Health data — step counts, workout logs, heart rate records, sleep patterns — is vulnerable to irreversible loss if you don't back it up first. Samsung Health manages data through two methods: cloud synchronization via your Samsung account, and local data export to CSV files. Knowing how each works before you wipe your phone prevents gaps in your health history.

## How Samsung Cloud Sync Works

Samsung Health's primary backup method is automatic cloud synchronization. When enabled, your health data is backed up to your Samsung account continuously. On a new device, signing into the same Samsung account within the Samsung Health app restores all historical data seamlessly — no manual steps required.

To verify cloud sync is active:

1. Open **Samsung Health**.
2. Tap the **three-line menu** (top-left or top-right depending on your device).
3. Select **Settings**.
4. Look for **Sync with Samsung Cloud** or **Sync data** and confirm the toggle is on.
5. You can also manually trigger a sync from this menu before resetting your phone.

This is the recommended method for transferring data to a new Samsung device, as the restored data integrates directly into the app. Always manually sync immediately before a factory reset, not just a few days before.

## How to Export Samsung Health Data as CSV

For users who want a local copy of their health records — or who are moving away from Samsung entirely — the data export function generates CSV files containing your tracked metrics.

1. Open **Samsung Health**.
2. Tap the **three-line menu** and select **Settings**.
3. Scroll down and tap **Download personal data** (labeled "Export data" or "Data management" on some versions).
4. Confirm the export when prompted.
5. The app will begin compiling your health records. Duration depends on how much data you've accumulated — keep your phone connected to Wi-Fi and plugged in if possible.
6. Once complete, the CSV files are saved to your device's internal storage, typically in a **Samsung Health** or **Download** folder, accessible via any file manager app.

A few limitations to be aware of: the exported CSV files cannot be re-imported back into Samsung Health. They are intended as a personal archive, not a restoration mechanism. Some fields use internal abbreviations that aren't self-explanatory without cross-referencing Samsung's export documentation. If the download stalls or returns a server error, update the Samsung Health app and try again after a device restart.

## What to Do With Your Exported Data

Once exported, the CSV files can be opened in Microsoft Excel, Google Sheets, or LibreOffice Calc. They contain detailed records across each tracked category — activity, sleep, heart rate, and so on — with timestamps that make it straightforward to identify trends over time.

Before resetting your phone, move these files to a secure external location:

- **Cloud storage:** Google Drive, OneDrive, or Dropbox are reliable options that make the files accessible regardless of what device you use next.
- **Personal computer:** Transferring via USB or Bluetooth provides an offline backup independent of any cloud service.
- **External drive:** Useful if you're archiving long-term health data and don't want to rely on a subscription-based cloud service.

These exported files won't restore your data inside Samsung Health, but they give you a permanent record that remains accessible even if Samsung's cloud service changes or your account access is ever disrupted.

## Connecting Samsung Health to Google Health Connect

If you're switching from a Samsung device to a non-Samsung Android phone, Google Health Connect offers a way to carry some of your health data forward. Samsung Health can sync data to Health Connect — a platform built into Android 14 and later that aggregates health data from multiple apps.

To enable the sync:

1. Open **Samsung Health**.
2. Go to **Settings > Connected services**.
3. Tap **Google Health Connect** and enable the connection.
4. Select which data types to share: steps, heart rate, sleep, calories, workouts, and more.

Once connected, apps on your new device that support Health Connect — such as Google Fit, Garmin Connect, or Strava — can read this data going forward. Note that this sync is ongoing, not a one-time export, and historical data depth varies by data type. Some categories sync up to 30 days of history; others may transfer more depending on the app.

## Checking What Data Actually Transfers

Not all Samsung Health data types carry over equally. Before a device switch, it's worth confirming which categories are included in your backup:

| Data Type | Samsung Cloud Sync | CSV Export | Health Connect |
|-----------|-------------------|-----------|----------------|
| Steps | ✅ | ✅ | ✅ |
| Heart Rate | ✅ | ✅ | ✅ |
| Sleep | ✅ | ✅ | ✅ |
| Workouts | ✅ | ✅ | ✅ |
| Nutrition | ✅ | ✅ | ❌ |
| Blood Pressure | ✅ | ✅ | ✅ |
| Samsung-specific metrics | ✅ | ✅ | ❌ |

Samsung-specific metrics — such as BIA body composition data from Galaxy Watch, or certain advanced sleep stage breakdowns — are only available within the Samsung Health ecosystem and do not transfer to third-party apps via Health Connect.

## Before You Factory Reset: Checklist

1. Manually trigger a Samsung Health cloud sync from Settings.
2. Export your data as CSV and confirm the files appear in your storage.
3. Move the CSV files to at least one external location (cloud or computer).
4. If switching to a non-Samsung Android device, enable Health Connect sync before wiping the phone.
5. Sign into Samsung Health on your new device with the same Samsung account to restore data from the cloud.

The combination of cloud sync for seamless restoration and CSV export for long-term archiving covers both scenarios — switching to a new Galaxy device and keeping a backup independent of Samsung's ecosystem.

---
Sources:
- [Samsung Health — Data Management](https://www.samsung.com/us/support/answer/ANS00088235/)
- [Samsung Cloud — Backup and Restore](https://www.samsung.com/us/support/answer/ANS00048603/)
- [Samsung Health CSV Export Documentation](https://developer.samsung.com/health/android/data/guide/data-export.html)
- [Google Health Connect — Overview](https://health.google/health-connect-android/)
