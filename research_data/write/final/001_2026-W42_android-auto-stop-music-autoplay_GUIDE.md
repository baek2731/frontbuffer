# How to Stop Android Auto From Playing Music Automatically

You start the car, your phone connects to Android Auto, and whatever you played last starts blasting through the speakers. Android Auto has a setting for this, but it is named differently from what many people search for, its location changes by phone brand, and several users report that music still starts after they turn it off. This guide covers the setting, where it lives, and what to check when it does not work.

## Turn off "Start music automatically"

The setting is a toggle called **Start music automatically**. On Xiaomi phones, Xiaomi's support page says turning it on makes the car [resume your last-played song or podcast when you start driving](https://www.mi.com/global/support/faq/details/KA-537920/). Turning it off stops that behavior. One Spotify Community thread quotes the toggle's description as "Automatically start media when you start driving."

1. Open your phone's **Settings** and search for **Android Auto**, then open it. [Android Central describes this route](https://www.androidcentral.com/apps-software/android-auto/5-android-auto-settings-i-always-change-on-any-new-android-phone).
2. Scroll to the **Start-up** section and switch **Start music automatically** off.
3. Connect to your car. Android Central says the music should now be in a paused state when you connect.

The location of the menu is not the same everywhere:

- Android Central puts the toggle under a **Start-up** sub-menu.
- How-To Geek says to look in the [**General** section](https://www.howtogeek.com/android-auto-became-more-useful-after-i-stopped-using-these-google-defaults/) of Android Auto's settings.
- Guiding Tech gives the route [Settings, Connected devices, Connection preferences, Android Auto](https://www.guidingtech.com/how-to-stop-music-from-automatically-playing-in-car/).
- Xiaomi's page gives Settings, then More connectivity options, then Android Auto.

These sources disagree on the section name and the route, so the menu labels on your phone may differ. The Settings search bar is the fastest way to reach it. A Symfonium support reply also notes that on some versions the toggle may be labeled **Resume media playback**.

## If the music still starts

Several people report that the toggle did not help. In a Spotify Community thread, users say they had the setting off and the music [still began as soon as they connected](https://community.spotify.com/t5/Android/Disable-autoplay-on-Android-auto/m-p/5492443/highlight/true). Comments under the Guiding Tech guide say the same.

Here is what the sources checked say about why:

- The developer of the Symfonium music app says that an app which receives a play command will play, and [it cannot know the command came from Android Auto](https://support.symfonium.app/t/stop-android-auto-from-playing-automatically/8662). That points at something sending the command, not at a missing setting. The reply does not say what.
- One user in the Spotify thread reported that stopping Spotify from playing in the background was what ended the automatic start. That is a single user's report, and neither Google nor Spotify confirms it in the pages checked.
- Another user wrote that their car has no setting to disable it.

None of this is confirmed by Google. No Google help page naming this toggle turned up in the searches done for this article. The steps below are things to try, not documented fixes.

1. **Check the music app's own settings** for autoplay or background-play options, since the app is the one that starts playing.
2. **Check your car's infotainment settings** for an autoplay or resume option, if your car has one.
3. **Find out what triggers it.** Connect once by cable and once wirelessly, and watch whether music starts before Android Auto appears on the screen or only after it launches. If it starts before, the trigger is more likely the car or the app than Android Auto's toggle.

## What to expect

Treat the toggle as the first and cheapest fix, and treat a failure as a sign of a different trigger. If your music app is the only one that ever starts by itself, start with that app's settings, not Android Auto's.

Checked October 15, 2026 against the sources listed below. Not tested on a phone or in a car.

---
Sources:
- [5 Android Auto settings I always change on any new Android phone, Android Central](https://www.androidcentral.com/apps-software/android-auto/5-android-auto-settings-i-always-change-on-any-new-android-phone)
- [Android Auto became more useful after I stopped using these 4 Google defaults, How-To Geek](https://www.howtogeek.com/android-auto-became-more-useful-after-i-stopped-using-these-google-defaults/)
- [How to Stop Music From Automatically Playing in Apple CarPlay and Android Auto, Guiding Tech](https://www.guidingtech.com/how-to-stop-music-from-automatically-playing-in-car/)
- [How to set the car to play music automatically when starting to drive using Android Auto, Xiaomi Support](https://www.mi.com/global/support/faq/details/KA-537920/)
- [Disable autoplay on Android auto, Spotify Community](https://community.spotify.com/t5/Android/Disable-autoplay-on-Android-auto/m-p/5492443/highlight/true)
- [Stop Android Auto from playing automatically, Symfonium support](https://support.symfonium.app/t/stop-android-auto-from-playing-automatically/8662)
