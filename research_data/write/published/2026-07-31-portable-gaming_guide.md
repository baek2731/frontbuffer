---
layout: single
title: 'How to Use Sunshine and Moonlight to Stream PC Games to Android'
date: 2026-07-31 14:02:00 +0000
last_modified_at: 2026-10-20 00:00:00 +0000
categories: [gaming]
tags: ["guide", "portable", "gaming"]
excerpt: 'Sunshine runs on your gaming PC and Moonlight on your Android tablet. Install both, pair them with a PIN, and fix choppy video, black screens and remote access.'
header:
  image: https://images.frontbuffer.net/posts/portable-gaming_guide/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

Sunshine on your gaming PC and Moonlight on your Android tablet let you play PC games over your home network. Sunshine is the host, Moonlight is the client, and pairing works through a PIN you type into Sunshine's web page. Below are the setup steps, how to reach the PC away from home, and the fixes the Moonlight docs list when the stream stutters or stays black.

*Checked October 20, 2026 against the Moonlight docs (Setup Guide edited February 2025, FAQ and Troubleshooting pages last edited in 2024), Sunshine's current documentation and NVIDIA's GameStream notice. Some Moonlight pages predate recent Sunshine releases, and nothing here was tested on a tablet or PC.*

---

## Why Sunshine

Moonlight began as an unofficial client for NVIDIA's GameStream, which ran inside GeForce Experience. [NVIDIA's notice](https://nvidia.custhelp.com/app/answers/detail/a_id/5436), updated in January 2023, said an update starting in mid-February would remove GameStream from the NVIDIA Games app on SHIELD devices. [Moonlight's FAQ](https://github.com/moonlight-stream/moonlight-docs/wiki/Frequently-Asked-Questions) now recommends Sunshine for hosting. It says Sunshine supports more platforms and GPUs than GeForce Experience and, unlike it, is still getting new features and fixes. The Moonlight team also keeps a [separate FAQ](https://github.com/moonlight-stream/moonlight-docs/wiki/NVIDIA-GameStream-End-Of-Service-Announcement-FAQ) on what the shutdown means for its clients.

---

## What you need

- **Host PC:** The [Moonlight Setup Guide](https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide) lists any modern AMD, NVIDIA or Intel GPU, Windows 10 or 11 (7 and 8 are not supported), macOS 12 or newer (experimental), or Linux (Debian 11, Ubuntu 22.04, Fedora 38 and newer).
- **Hardware encoding:** [Sunshine's documentation](https://docs.lizardbyte.dev/projects/sunshine/latest/) lists 4GB of RAM as a minimum, plus a GPU with a hardware encoder: AMD VCE 1.0 or newer, an NVENC-capable Nvidia card, or on Windows an Intel GPU from Skylake on with QuickSync. It warns that its requirements table is a work in progress and should not drive hardware purchases.
- **Tablet:** Android 4.1 or newer. The Setup Guide says newer, faster devices are more likely to stream smoothly.
- **Network:** The Setup Guide strongly recommends 5 GHz Wi-Fi 5 or Wi-Fi 6 on the tablet and a wired connection from the PC to the router.

---

## Set up Sunshine and Moonlight

1. **Install Sunshine on the PC.** Sunshine's [Getting Started page](https://docs.lizardbyte.dev/projects/sunshine/latest/md_docs_2getting__started.html) recommends the installer from the [latest release](https://github.com/LizardByte/Sunshine/releases/latest) on Windows. Per its [release notes](https://github.com/LizardByte/Sunshine/releases/tag/v2026.914.233613), the September 15, 2026 release includes a high-severity security fix for Linux hosts, so update if you run Linux. The Moonlight guide says the PC may need a reboot afterward for controller emulation to work.
2. **Open the web interface.** Go to `https://localhost:47990` or use "Open Sunshine" in the tray menu. Sunshine's docs say to ignore the browser's insecure-site warning, which comes from a self-signed certificate. On first start Sunshine asks you to create a username and password. Keep them: the Moonlight guide notes that anyone with access to this page can add clients that reach your computer remotely.
3. **Install Moonlight on the tablet** from [Google Play](https://play.google.com/store/apps/details?id=com.limelight). Connect the tablet to the same network as the PC. The PC should appear in Moonlight within a few seconds, or you can add it by IP address.
4. **Pair with a PIN.** Tap the PC in Moonlight and it shows a PIN. In Sunshine's web interface, open **PIN** in the top bar, type the PIN, press Enter, and name the device. Pairing happens over the network, not Bluetooth.
5. **Start a game.** Sunshine comes with Steam and a Desktop entry. Add other games under Applications in the web interface.

Two behaviors surprise new users. Leaving a stream does not close the game. Per Moonlight's FAQ, select the running app and choose **Quit App** to end the session, which closes the app on the PC, so save first. Sunshine's docs also say that starting an app while another one is running terminates the running one.

---

## Controllers

Moonlight for Android supports gamepads that use the standard Android button mapping, plus some popular controllers including Xbox 360, Xbox One, PS3 and PS4 pads. The Setup Guide suggests testing yours first, because some have latency or disconnection problems, particularly PlayStation controllers over Bluetooth. [Moonlight's Troubleshooting page](https://github.com/moonlight-stream/moonlight-docs/wiki/Troubleshooting) adds that on some devices an active Bluetooth connection can hurt streaming because of antenna wiring.

On a Windows host, Sunshine's docs describe two virtual gamepad backends. ViGEmBus has reached end of life and emulates only Xbox 360 and DualShock 4 pads. The Virtual HID Driver supports more controller types but requires a paid machine license for its driver-backed devices. This guide did not test either.

---

## Stream away from home

Moonlight recommends pairing at home first. Sunshine has a built-in UPnP option in the Network section of its settings that forwards the required ports automatically. If that does not work, the Setup Guide covers ZeroTier, Tailscale and NordVPN Meshnet, and lists the ports to forward manually.

Per the FAQ, Sunshine 0.22 and later support end-to-end encryption, and full encryption is on by default for capable devices when streaming over the Internet. The FAQ also suggests setting the bitrate at least 1 Mbps below your upload speed, and its latency notes say cellular networks tend to add delay.

---

## Picture settings

Moonlight lets you choose resolution, frame rate and bitrate. Its bitrate slider stops at 150 Mbps, which the FAQ attributes to encoder and decoder limits. A low frame rate on a still screen is normal with Sunshine: it uses variable frame rate encoding, and the FAQ says static content can drop to around 10 FPS, rising again as the picture changes.

HDR has conditions. Sunshine officially supports HDR on Windows hosts whose GPU encodes HEVC Main 10 or AV1 10-bit, with HDR active on the PC (an HDR display or an EDID emulator dongle) and enabled in Moonlight. The Setup Guide adds that an Android client needs Android 7.0 or newer, a HEVC Main10 hardware decoder and an HDR10 display.

---

## Troubleshooting

**Cannot connect or pair on your home network.** [Moonlight's Troubleshooting page](https://github.com/moonlight-stream/moonlight-docs/wiki/Troubleshooting) suggests this order:

1. Reboot the PC and the tablet.
2. If the PC is on both Ethernet and Wi-Fi, disconnect all but the fastest connection.
3. Turn off any VPN on the PC. You may also need to disable the VPN's setting that blocks local network access.
4. Disable the PC's firewall and antivirus to test. If streaming works, create an exception. The Setup Guide lists the Windows firewall rules and says Sunshine normally creates them.
5. Make sure a monitor, or an HDMI headless dongle, is connected and turned on, and that you are logged in.

**Choppy or laggy video.** Put the tablet on 5 GHz Wi-Fi and the PC on Ethernet, lower the bitrate, try 720p at 30 FPS, and test with Bluetooth off. The FAQ says dropped frames are common on 2.4 GHz Wi-Fi and powerline networking.

**Black screen.** Check that the monitor or dongle is on and connected to the GPU. Try a different game or Steam, or stream the Desktop entry and start the game from there.

**Still stuck.** Sunshine's web interface has a Troubleshooting tab with logs, and the Moonlight docs point to their Discord server for help.

---

## Takeaway

Pair on your home network first, with the PC on Ethernet and the tablet on 5 GHz Wi-Fi. If the picture is rough, lower the bitrate before changing anything else.

---

Sources:
- [Setup Guide, Moonlight Documentation](https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide)
- [Frequently Asked Questions, Moonlight Documentation](https://github.com/moonlight-stream/moonlight-docs/wiki/Frequently-Asked-Questions)
- [Troubleshooting, Moonlight Documentation](https://github.com/moonlight-stream/moonlight-docs/wiki/Troubleshooting)
- [NVIDIA GameStream End Of Service Announcement FAQ, Moonlight Documentation](https://github.com/moonlight-stream/moonlight-docs/wiki/NVIDIA-GameStream-End-Of-Service-Announcement-FAQ)
- [GameStream End of Service Notification, NVIDIA Support](https://nvidia.custhelp.com/app/answers/detail/a_id/5436)
- [Sunshine documentation, LizardByte](https://docs.lizardbyte.dev/projects/sunshine/latest/)
- [Getting Started, Sunshine documentation](https://docs.lizardbyte.dev/projects/sunshine/latest/md_docs_2getting__started.html)
- [Release v2026.914.233613, Sunshine on GitHub](https://github.com/LizardByte/Sunshine/releases/tag/v2026.914.233613)
