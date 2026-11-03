# Can Moonlight Stream Over the Internet? UPnP, VPN and Ports

Yes. Moonlight's own guide describes several ways to stream away from home with Sunshine. The simplest is Sunshine's built-in UPnP option, which is turned off by default and which asks your router to open the needed ports. The others are manual port forwarding and private-network tools such as Tailscale, ZeroTier and NordVPN Meshnet. Which one works depends mostly on your router and your internet provider.

*Checked November 3, 2026 against Moonlight's Setup Guide (last edited February 27, 2025) and its Internet Streaming Errors page, Sunshine's current Configuration page and the Sunshine v0.20.0 release notes.*

## Before you start

Moonlight's [Setup Guide](https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide) recommends pairing Moonlight with your gaming PC on your home network first, before trying the internet. On iPhone, iPad and Apple TV you must pair on the same network, which the guide ties to Apple's guidelines.

## Option 1: Sunshine's UPnP

Sunshine's [Configuration page](https://docs.lizardbyte.dev/projects/sunshine/latest/md_docs_2configuration.html) describes the `upnp` setting as Sunshine attempting to open ports for streaming over the internet, and it is disabled by default. The Setup Guide says you can turn it on in the Network section of the settings in Sunshine's web UI, and that it forwards the required ports automatically.

Its troubleshooting tips say to make sure UPnP is enabled in your router settings and to delete any older Moonlight port forwarding entries. The [Sunshine v0.20.0 release notes](https://github.com/LizardByte/Sunshine/releases/tag/v0.20.0) add that the older Moonlight Internet Hosting Tool is not needed with Sunshine, and that if it is installed you should remove it or update it to version 5.6 or later to avoid conflicts.

## Option 2: Manual port forwarding

If UPnP does not work, the guide lists TCP 47984, 47989 and 48010 and UDP 47998, 47999, 48000, 48002 and 48010 to forward to your gaming PC. It says to use the same value for internal and external ports, and to give the PC a static DHCP reservation so the forwards keep pointing at the right machine. You can test ports 47984 and 47989 with canyouseeme.org. If Moonlight did not find your PC automatically, open whatsmyip.org on the PC and type that address into Moonlight.

## Option 3: A private network instead of open ports

The guide recommends these when direct forwarding fails, for example behind a Carrier-Grade NAT, with two routers, or on a network that blocks Moonlight.

- **ZeroTier.** It acts like a VPN, and the guide says the free service is fine for Moonlight. It needs software running and connected on both the host and every client whenever you stream.
- **Tailscale.** The guide says streaming only works if the devices connect directly. If Tailscale falls back to a shared relay, you cannot stream, and the guide asks users not to push heavy traffic through it. Some mobile networks may block or interfere with the UDP packets, and it names T-Mobile in the US. You may need to add the Tailscale `100.x.x.x` address or its hostname to Moonlight by hand.
- **NordVPN Meshnet.** The guide says it lets you skip port forwarding and get around CGNAT, and that an active NordVPN subscription is not required. We did not check whether Meshnet is still offered.

## Why it can fail

Moonlight's [Internet Streaming Errors page](https://github.com/moonlight-stream/moonlight-docs/wiki/Internet-Streaming-Errors), which explains messages from Moonlight's internet testing tool, gives these causes:

- **More than one router.** Restart the router. If that does not help, the cause may be a Carrier-Grade NAT on your provider's network.
- **Carrier-Grade NAT.** Your provider has not given you a public IP address. The page says many providers will give one for free if you ask, which we could not confirm for any particular provider. It also notes that a connection with IPv6 can work for hosting, but only for clients on networks that also support IPv6.
- **A firewall** on the host PC blocking the tool from talking to your router.
- **A locked PC or hibernation.** A PC sitting at the lock screen, including when you tested it over Microsoft Remote Desktop, or configured to hibernate, will not work for streaming.

## Encryption and mobile data

Sunshine's Configuration page says `wan_encryption_mode` defaults to 1, meaning encryption is used when the client supports it. The other choices are 0, no encryption, and 2, encryption mandatory. It warns that encryption can reduce streaming performance on weaker hosts and clients. The Setup Guide suggests lowering resolution and bitrate when streaming over a mobile network.

## What we could not confirm

- Whether your router supports UPnP, or how your provider handles public IP addresses.
- The exact labels in the Sunshine web UI of your version.
- Real-world streaming quality away from home. We did not measure it.

---
Sources:
- [Setup Guide, Moonlight Docs](https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide)
- [Internet Streaming Errors, Moonlight Docs](https://github.com/moonlight-stream/moonlight-docs/wiki/Internet-Streaming-Errors)
- [Configuration, Sunshine documentation, LizardByte](https://docs.lizardbyte.dev/projects/sunshine/latest/md_docs_2configuration.html)
- [Sunshine v0.20.0 release notes, GitHub](https://github.com/LizardByte/Sunshine/releases/tag/v0.20.0)

<!-- excerpt: Moonlight can stream away from home with Sunshine's UPnP, a VPN-style tool or manual port forwarding. How each works and why CGNAT blocks some setups. -->
<!-- tags: guide, moonlight, sunshine, remote-streaming -->
