# How to Customize Android Quick Settings Tiles

The Quick Settings panel — the grid of toggles that appears when you swipe down twice from the top of your screen — ships with a default layout that rarely matches how anyone actually uses their phone. Moving the tiles you use most to the front row takes about two minutes and saves real time every day.

### Opening the Editor

Swipe down twice from the top of the screen to expand the full Quick Settings panel. In the bottom-left corner, tap the **pencil icon** (Edit). On some Android skins — Samsung One UI, for example — this icon may appear as "Edit" text instead.

The editor splits into two sections: your active tiles at the top and inactive (available but hidden) tiles below.

### Rearranging, Adding, and Removing Tiles

**To move a tile:** Long-press it and drag it to a new position in the active grid. Tiles in the first row are visible without expanding the panel — put your most-used toggles there.

**To add a tile:** Scroll down to the inactive section, long-press the tile you want, and drag it into the active grid.

**To remove a tile:** Long-press it in the active section and drag it down to the inactive area.

Tap **Done** (or the back button, depending on your Android version) when finished.

### What to Put in the First Row

The first two to four tiles show without swiping. Common high-value placements:

- **Wi-Fi** and **Bluetooth** — toggled constantly when moving between locations
- **Do Not Disturb** — faster than navigating Settings when you need focus
- **Flashlight** — the tile most people reach for in a hurry
- **Screen record** or **Hotspot** — useful if you use these regularly

Remove tiles you never tap: NFC, Nearby Share, and Auto-rotate are commonly present by default but rarely needed on demand.

### Android 12 and Later: Brightness Slider Placement

Starting with Android 12, Google moved the brightness slider to the top of the Quick Settings panel, above the tiles. On stock Android 12 through Android 16, the slider stays there — it is not repositionable through the standard editor.

Samsung One UI gives more flexibility: the brightness slider can be moved to below the notification bar (above Quick Settings) or positioned within the panel. Access this via **Settings > Display > Status bar** on One UI 6 and later.

### Android 16 QPR1: Resizable Tiles

Android 16 QPR1, released in May 2025, introduced the ability to resize individual Quick Settings tiles. Each tile can be toggled between a compact 1×1 size and a wider 2×1 pill shape directly from the editor.

**To resize a tile:**
1. Enter edit mode by tapping the pencil icon.
2. Tap anywhere inside the tile you want to resize.
3. A drag handle appears on the right edge of the tile.
4. Drag left to shrink to 1×1 (label hidden), or right to expand to 2×1 (label visible).

With 1×1 tiles, you can fit up to four toggles per row instead of the default two or three, which is useful for keeping more controls visible without expanding the panel. Android 16 QPR1 also reorganized the tile editor itself — tiles are now grouped by category (Connectivity, Utilities, Display, Privacy, Accessibility, From apps) rather than appearing in a single unsorted list, which makes finding less common tiles considerably faster.

### Third-Party Tiles

Apps can add their own Quick Settings tiles. Spotify, Shazam, and various VPN apps register tiles that appear in the inactive section after installation. Add them the same way as system tiles — long-press and drag into the active grid.

To remove a third-party tile completely (not just hide it), you need to uninstall the app or revoke the tile permission under **Settings > Apps > [App name] > Other permissions > Add Quick Settings tiles**.

### Pixel-Specific: Custom Tiles

On Pixel phones running Android 13 and later, you can create custom Quick Settings tiles that trigger specific app shortcuts using apps like Tasker or MacroDroid. These appear in the inactive section like any other tile once configured in the respective app.

### Samsung One UI: Additional Options

One UI provides a few customization options that stock Android does not. In addition to the brightness slider repositioning mentioned above:

- **Panel style:** One UI 6 and later lets you switch between a full-panel Quick Settings layout (notifications and tiles separated) and a combined single-pull layout. Go to **Settings > Notifications > Notification panel style**.
- **Button order reset:** If your layout gets cluttered, tap **Reset** inside the editor to return to Samsung's default tile arrangement without needing to drag tiles individually.
- **Good Lock — QuickStar module:** Samsung's Good Lock app includes a QuickStar module that unlocks deeper Quick Settings customization, including custom backgrounds, transparency controls, and additional layout options not available in the standard editor.

### Troubleshooting: Tile Changes Not Saving

On some devices, Quick Settings edits revert after a reboot. This typically happens when a device management policy (common on work profiles or MDM-managed phones) restricts panel customization. If you're on a personal device and seeing this behavior, check whether your phone has an active work profile under **Settings > Accounts** and whether the MDM policy restricts Quick Settings. Clearing the SystemUI cache (**Settings > Apps > Show system apps > System UI > Storage > Clear cache**) can also resolve occasional save failures.

---

Sources:
- [Android — Customize Quick Settings](https://support.google.com/android/answer/9083864)
- [Android Authority — Quick Settings guide](https://www.androidauthority.com/android-quick-settings-3209902/)
- [Samsung — One UI Quick Settings](https://www.samsung.com/us/support/answer/ANS00088226/)
- [9to5Google — Android 16 QPR1 Quick Settings resizing](https://9to5google.com/2025/05/android-16-qpr1-quick-settings/)
