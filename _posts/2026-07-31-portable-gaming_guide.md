---
layout: single
title: 'How to Stream PC Games to Your Android Tablet with Moonlight and Sunshine'
date: 2026-07-31 14:02:00 +0000
categories: [gaming]
tags: ["guide", "portable", "gaming"]
excerpt: 'Nvidia ended its GameStream service on February 27, 2023, leaving SHIELD owners without a built-in streaming solution. The open-source combination of…'
header:
  image: https://images.frontbuffer.net/posts/portable-gaming_guide/og.png
  overlay_filter: 0
author_profile: false
read_time: true
share: true
---

Nvidia ended its GameStream service on February 27, 2023, leaving SHIELD owners without a built-in streaming solution. The open-source combination of Sunshine (server) and Moonlight (client) has become the standard replacement — and for most setups, it performs better than the proprietary service it replaced.

This guide covers everything needed to get PC games streaming to an Android tablet.

---

## How It Works

Sunshine runs on your gaming PC and acts as the stream host. Moonlight runs on your Android tablet and connects to it. Sunshine implements Nvidia's GameStream protocol but works with AMD, Intel, and Nvidia GPUs — not just GeForce hardware.

The connection uses Bluetooth for initial pairing and Wi-Fi for data. For best results, your PC should be on wired Ethernet and your tablet on 5GHz Wi-Fi.

---

## PC Requirements (Sunshine Host)

| Component | Minimum | Recommended for 4K |
|---|---|---|
| OS | Windows 10, macOS 12, Ubuntu 22.04+ | Same |
| CPU | Intel Core i3 / AMD Ryzen 3 | i5 / Ryzen 5 or better |
| RAM | 4GB | 8GB+ |
| GPU (Nvidia) | GTX 600 series+ (NVENC) | GTX 1080+ |
| GPU (AMD) | VCE 1.0+ | VCE 3.1+ |
| GPU (Intel) | Skylake+ with QuickSync | HD Graphics 510+ |
| Network | Wi-Fi | Wired Ethernet |

---

## Setup

**1. Install Sunshine on your PC**

Download Sunshine from [lizardbyte.dev/sunshine](https://lizardbyte.dev/sunshine/) or the [GitHub releases page](https://github.com/LizardByte/Sunshine/releases). After installation, Sunshine's web UI is accessible at `https://localhost:47990` — use this for configuration and pairing.

**2. Install Moonlight on your Android tablet**

Download [Moonlight Game Streaming](https://play.google.com/store/apps/details?id=com.limelight) from the Google Play Store.

**3. Pair the devices**

Open Moonlight on your tablet. If both devices are on the same network, your PC should appear automatically. If not, add it manually using the PC's local IP address. Moonlight will display a PIN — enter it into the Sunshine web UI to complete pairing.

---

## Remote Access and Security

Streaming outside your home network requires port forwarding, which opens your router to the internet. The Moonlight documentation recommends using a VPN or zero-trust solution like [Tailscale](https://tailscale.com/) or [Twingate](https://www.twingate.com/) instead — these create an encrypted tunnel that makes your devices appear on the same local network without exposing any ports.

Note that your ISP may periodically change your external IP address, which can break port forwarding rules. Dynamic DNS services can handle this automatically if you go the port forwarding route.

---

## Performance

Moonlight supports up to 4K resolution with HDR at up to 120fps on capable hardware and networks. Users consistently report latency that feels "almost unnoticeable" on well-configured local setups.

Key factors affecting performance:
- **Host GPU**: Hardware encoding (NVENC, VCE, QuickSync) is essential. Software encoding works as a fallback but increases CPU load and latency.
- **Network**: Wired Ethernet on the PC side is the single biggest quality-of-life improvement. 5GHz Wi-Fi on the tablet side matters significantly for 1080p+ streaming.
- **Bitrate**: Higher bitrate means sharper image but requires more bandwidth. Start at the default and adjust based on your network.

---

## Troubleshooting

**Can't connect or pair**
Check firewall settings on the host PC. Ensure both devices are on the same network or VPN. Verify the PC's IP address. Reboot both devices.

**Choppy or laggy video**
Switch the PC to wired Ethernet. Move the tablet closer to the router or switch to 5GHz. Lower bitrate, resolution, or frame rate in Moonlight settings. Check for background processes consuming GPU resources on the host.

**Black screen / no video**
Ensure the primary monitor on the host PC is on and you're logged in. Update GPU drivers. If hardware-accelerated GPU scheduling is enabled, try disabling it.

**Controller input issues**
Verify gamepad compatibility with your Android device. Bluetooth controllers can occasionally drop or lag — USB-C wired connection to the tablet eliminates this.

---

Sources:
- [Moonlight Game Streaming — FAQ](https://github.com/moonlight-stream/moonlight-docs/wiki/Frequently-Asked-Questions)
- [Moonlight — Setup Guide](https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide)
- [Sunshine — Official Site](https://lizardbyte.dev/sunshine/)
- [Sunshine — System Requirements](https://docs.lizardbyte.dev/projects/sunshine/en/latest/about/system_requirements.html)
- [Moonlight — Troubleshooting](https://github.com/moonlight-stream/moonlight-docs/wiki/Troubleshooting)
- [Twingate — Sunshine Remote Gaming](https://www.twingate.com/docs/sunshine-remote-game-streaming/)
- [Nvidia GameStream End of Service FAQ](https://github.com/moonlight-stream/moonlight-docs/wiki/NVIDIA-GameStream-End-Of-Service-Announcement-FAQ)
