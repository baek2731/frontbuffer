# Sunshine and Moonlight Ports and Firewall: What to Open

Sunshine builds all of its ports from one starting number, 47989 by default. For manual forwarding, Moonlight's own guide lists TCP 47984, 47989 and 48010, plus UDP 47998, 47999, 48000, 48002 and 48010. On a home network, Sunshine should create the Windows Firewall rules itself, and the web UI port, TCP 47990, is not on the forwarding list. This post covers what each port does, how to add the rules by hand and which settings matter when a stream will not connect.

*Checked November 3, 2026 against Sunshine's current Configuration page, an older Sunshine Advanced Usage page (v0.22.1) for the port table, and Moonlight's Setup Guide (last edited February 27, 2025).*

## The ports

Sunshine's [Configuration page](https://docs.lizardbyte.dev/projects/sunshine/latest/md_docs_2configuration.html) says the `port` setting sets the family of ports Sunshine uses. The default is 47989, the allowed range is 1029 to 65514, and changing it offsets the other ports as shown in the web UI. The current page does not repeat the offset table. An [older Advanced Usage page (v0.22.1)](https://docs.lizardbyte.dev/projects/sunshine/v0.22.1/about/advanced_usage.html) does:

| Purpose | Default port | Offset from `port` |
|---|---|---|
| HTTPS | 47984 TCP | -5 |
| HTTP | 47989 TCP | 0 |
| Web UI | 47990 TCP | +1 |
| RTSP | 48010 TCP | +21 |
| Video | 47998 UDP | +9 |
| Control | 47999 UDP | +10 |
| Audio | 48000 UDP | +11 |

That older page also warns that custom ports may not be supported by all Moonlight clients. Moonlight's guide additionally lists UDP 48002 and UDP 48010, which are not in the older Sunshine table, so check your Sunshine web UI for the ports your version uses.

## The web UI port stays local

Sunshine's web UI opens at `https://localhost:47990`. Moonlight's [Setup Guide](https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide) says the browser will show a "not secure" warning you can safely ignore, and that the first launch asks you to create an account. It stresses this is important because anyone with access to that interface can add new clients that reach your computer remotely.

The `origin_web_ui_allowed` setting controls who can open it. Its default is `lan`. The choices are `pc` (only localhost), `lan` (only devices on your local network) and `wan` (anyone). The forwarding lists in Moonlight's guide do not include 47990. Our reading of those two pages is that there is no reason to forward it to the internet.

## Add the Windows Firewall rules by hand

The Setup Guide says Sunshine should create Windows Firewall rules automatically. If streaming fails even on the same network as your PC, it suggests first turning your firewall off briefly to confirm it is the cause, then turning it back on. If a firewall is the cause, the guide gives these two commands, which you run in an administrator Command Prompt or PowerShell window:

```
netsh advfirewall firewall add rule name="GameStream UDP" dir=in protocol=udp localport=5353,47998-48010 action=allow
netsh advfirewall firewall add rule name="GameStream TCP" dir=in protocol=tcp localport=47984,47989,48010 action=allow
```

Then check that your PC shows as online in Moonlight. For other firewall products, the guide says to allow TCP 47984, 47989 and 48010 and UDP 5353, 47998, 47999, 48000, 48002 and 48010.

## Testing a router forward

If you forward ports on a router, the guide says to use the same number for the internal and external port. To check, visit canyouseeme.org and test ports 47984 and 47989, which should report success. The other ports are only active while streaming, so Moonlight itself is the only way to test them.

## Settings worth knowing when a stream fails

All of these come from Sunshine's Configuration page.

- **`address_family`** defaults to `ipv4`. Set it to `both` for IPv4 and IPv6.
- **`bind_address`** is empty by default, so Sunshine binds to all network interfaces. You can set one address if you have several.
- **`ping_timeout`** defaults to 10000 milliseconds, the time Sunshine waits for data from Moonlight before it ends the stream.
- **`packetsize`** defaults to 0. The docs describe lowering it to avoid fragmentation on a low-MTU link and mention a layer 2 VPN with Android and iOS clients as an example, with a note to reduce the bitrate when using low values.

For the basic setup, see our guide to [using Sunshine and Moonlight to stream PC games to Android](https://frontbuffer.net/gaming/portable-gaming_guide/).

## What we could not confirm

- The exact port offsets in the latest Sunshine build, since the current page points to the web UI instead of a table.
- Why Moonlight lists UDP 48002 and 48010 while the older Sunshine table does not.
- Whether your Sunshine install created its own firewall rules, or how a third-party security suite treats them.

---
Sources:
- [Configuration, Sunshine documentation, LizardByte](https://docs.lizardbyte.dev/projects/sunshine/latest/md_docs_2configuration.html)
- [Advanced Usage (v0.22.1), Sunshine documentation, LizardByte](https://docs.lizardbyte.dev/projects/sunshine/v0.22.1/about/advanced_usage.html)
- [Setup Guide, Moonlight Docs](https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide)

<!-- excerpt: Which ports Sunshine and Moonlight use, what to open in Windows Firewall or on a router, and why the web UI port stays off the forwarding list. -->
<!-- tags: guide, sunshine, moonlight, firewall -->
