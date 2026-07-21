# How to Stream PC Games to Android Tablets using the Moonlight App

The ability to enjoy high-fidelity PC games from the comfort of an Android tablet offers a compelling blend of power and portability. Game streaming solutions have significantly evolved, allowing users to extend their desktop gaming experience to mobile devices with remarkable fidelity. This guide explores how to leverage open-source applications like the Moonlight app, paired with its server counterpart Sunshine, to stream PC games to Android tablets, drawing insights from official documentation and real-world user experiences.

### The Evolution of PC Game Streaming to Mobile

Historically, proprietary solutions such as Nvidia SHIELD offered integrated game streaming capabilities, allowing users to stream games from their GeForce-powered PCs to SHIELD devices. However, the landscape shifted significantly when Nvidia officially announced the discontinuation of its GameStream service. This service, which was a core feature of the Nvidia Games app, ceased support on February 27, 2023. This pivotal change prompted the gaming community to actively seek out robust, self-hosted, and open-source alternatives. The transition away from proprietary features has driven the widespread adoption of solutions that empower users to maintain full control over their streaming environment, with the combination of Sunshine and Moonlight emerging as a leading choice.

### Understanding Sunshine and Moonlight for Seamless Streaming

The modern game streaming ecosystem typically involves two primary components: a server application running on the powerful gaming PC and a client application installed on the portable device. For those aiming to stream PC games to a variety of devices, the pairing of Sunshine (the server) and Moonlight (the client) has become exceptionally popular, especially since Nvidia's discontinuation of GameStream. While some users might colloquially refer to the client as "Moonshine," its official and widely recognized name is Moonlight.

Sunshine is an open-source, self-hosted game stream host that implements Nvidia's GameStream protocol. It offers low-latency, cloud gaming server capabilities with broad support for hardware encoding across AMD, Intel, and Nvidia GPUs. Should dedicated hardware support be unavailable, software encoding acts as a reliable fallback. Moonlight, on the other hand, is an open-source client that allows users to connect to a Sunshine host and stream games. It is completely free, community-driven, and supports a wide array of client devices, including Android tablets, iOS devices, Apple TV, Windows, macOS, Linux, Raspberry Pi, ChromeOS, and even some smart TVs and gaming handhelds like the PS Vita and Nintendo Switch. This combination effectively allows users to create their own personal, high-performance cloud gaming server, delivering a remote desktop experience meticulously tailored for gaming.

### Setting Up Your Self-Hosted Game Streaming Environment

Setting up Sunshine and Moonlight is generally described as straightforward, though it requires careful attention to detail for optimal performance. The process involves installing Sunshine on your gaming PC and the Moonlight app on your Android tablet.

**System Requirements for the Host PC (Sunshine):**
To ensure a smooth streaming experience, your host PC should meet certain specifications:
*   **Operating System:** Windows 10 or later, macOS 12 or later, or a compatible Linux distribution (e.g., Ubuntu 22.04+). Windows Server is not officially supported due to limitations with virtual gamepads.
*   **CPU:** An Intel Core i3 or AMD Ryzen 3 processor or newer is recommended as a minimum. For 4K streaming, an Intel Core i5 or AMD Ryzen 5 or better is advisable.
*   **RAM:** A minimum of 4GB of RAM is required, with 8GB or more recommended for demanding games and higher resolutions.
*   **GPU:** Hardware encoding support is crucial for low-latency streaming.
    *   **Nvidia:** Any NVENC-enabled GeForce GTX/RTX GPU (600 series or newer). For 4K streaming, a GeForce GTX 1080 or better is suggested.
    *   **AMD:** VCE 1.0 or newer. VCE 3.1 or higher is recommended for 4K streaming.
    *   **Intel:** Skylake or newer with QuickSync encoding support on Windows, or VAAPI compatibility on Linux. HD Graphics 510 or newer is recommended for 4K.
*   **Network:** A wired Ethernet connection for the host PC is highly recommended for stability and bandwidth, especially for 4K streaming.

**Installation and Pairing:**
1.  **Install Sunshine on PC:** Download the Sunshine server from its official GitHub releases page or SourceForge. Follow the installation instructions for your operating system. Sunshine provides a web-based user interface (UI) for configuration and client pairing, typically accessible via `https://localhost:47990` on the host PC.
2.  **Install Moonlight on Android Tablet:** Download the Moonlight Game Streaming app from the Google Play Store.
3.  **Pairing:** Once Sunshine is running on your PC and Moonlight is installed on your tablet, open Moonlight. Your PC should ideally appear automatically in the list of available hosts if both devices are on the same local network. If not, you can manually add your PC using its local IP address. Moonlight will then display a PIN, which you'll enter into the Sunshine web UI on your PC to complete the secure pairing process.

**Network Configuration and Security:**
A critical aspect of enabling remote access for game streaming, particularly when connecting from outside the local network, involves port forwarding. This process, while necessary for some configurations, introduces an additional security risk by opening specific ports on your router to the internet. The official Moonlight documentation advises caution and recommends employing a strong, secure password for your streaming setup to mitigate potential vulnerabilities.

For enhanced security and to avoid direct port forwarding, users can explore alternatives such as Virtual Private Networks (VPNs) or Zero Trust Network Access solutions like Tailscale or Twingate. These solutions create a secure, encrypted tunnel between your client device and host PC, effectively making them appear as if they are on the same local network, even when geographically separated. This eliminates the need to expose your home network directly to the internet through port forwarding. Furthermore, users should be aware that their Internet Service Provider (ISP) might periodically change their external IP address, which could necessitate adjustments to port forwarding settings or dynamic DNS services over time. For optimal in-home streaming, ensuring your Android tablet is connected to a 5GHz Wi-Fi network and your PC is wired via Ethernet is highly recommended to minimize latency and maximize bandwidth.

### Performance and User Experience

One of the most crucial factors for an enjoyable game streaming experience is latency. Reports from users consistently indicate that the latency experienced with Sunshine and Moonlight setups can be "almost unnoticeable". This exceptionally low latency is vital for maintaining responsiveness and immersion, especially in fast-paced games, making the streamed experience feel remarkably close to playing directly on the PC. The overall performance is frequently described as "buttery smooth" and highly satisfying, suggesting that when properly configured, the system delivers a high-quality streaming experience that meets or even exceeds user expectations for fluidity and playability.

Factors influencing performance include the host PC's hardware encoding capabilities, network speed and stability, and the streaming settings (resolution, bitrate, frame rate) configured within Sunshine and Moonlight. Moonlight supports streaming at up to 4K resolution with HDR and up to 120 frames per second (FPS) on capable client devices and networks. Users can adjust bitrate settings to balance image quality with network conditions, with higher bitrates providing crisper visuals but requiring more bandwidth.

### Community Findings and Practical Considerations

The vibrant community surrounding self-hosted game streaming solutions like Sunshine and Moonlight highlights several key practical considerations for prospective users. Many have found the setup process to be remarkably easy to understand and implement, even for those new to such configurations. This ease of use is a significant draw for individuals seeking alternatives after the discontinuation of proprietary services like Nvidia GameStream.

On the performance front, consistent feedback points to a highly responsive and smooth streaming experience, with latency being a minimal concern for most users on well-configured networks. This positive reception underscores the effectiveness of the Sunshine/Moonlight pairing in delivering a gaming experience that closely mimics local play.

However, the community also emphasizes important security considerations. The necessity of port forwarding for remote access is acknowledged as a potential security risk. Users are strongly advised to take extra precautions, such as using strong, unique passwords and considering VPNs or Zero Trust solutions, to secure their setup. Additionally, the dynamic nature of ISP-assigned IP addresses is a practical detail that users should keep in mind, as it may require occasional updates to their network configurations or the use of dynamic DNS services.

**Troubleshooting Common Issues:**
Should you encounter issues, the Moonlight community and documentation offer extensive troubleshooting resources. Common problems and solutions include:
*   **Unable to connect/pair:** Check firewall settings on the host PC, ensure both devices are on the same network (or VPN), and verify the correct IP address. Rebooting both devices can often resolve initial connection problems.
*   **Choppy or laggy video:** Ensure your host PC is wired via Ethernet and your client is on a 5GHz Wi-Fi network. Lower the bitrate, resolution, or frame rate settings in Moonlight. Check for background applications consuming resources on the host PC.
*   **Black screen/no video:** Ensure your primary monitor on the host PC is turned on and you are logged in. Update GPU drivers. Disable hardware-accelerated GPU scheduling if enabled.
*   **Controller input issues:** Verify that your gamepad is compatible with your Android device and Moonlight. Some controllers may have latency or disconnection issues over Bluetooth.

### Conclusion

Streaming PC games to an Android tablet using the Moonlight app, powered by the Sunshine server, offers a powerful and flexible way to enjoy your gaming library with enhanced portability. The community's overwhelmingly positive experiences regarding setup ease, minimal latency, and high-quality visuals underscore the viability of this solution, especially for those seeking alternatives to discontinued proprietary services. While considerations like network security, dynamic IP addresses, and proper network configuration require attention, the overall sentiment points towards a highly effective and enjoyable game streaming experience. For deeper dives into optimizing your home network for streaming, consider exploring our guide on [INTERNAL LINK: optimizing home network for game streaming].

**Sources:**
*   [https://wccftech.com/nvidia-shield-ends-gamestream-service-recommends-steam-link-plus-geforce-now-as-replacements/](https://wccftech.com/nvidia-shield-ends-gamestream-service-recommends-steam-link-plus-geforce-now-as-replacements/)
*   [https://toolboost.io/blog/sunshine-streaming-host-specs](https://toolboost.io/blog/sunshine-streaming-host-specs)
*   [https://www.linustechtips.com/news/nvidia-kills-off-gamestream-feature-on-shield-devices/](https://www.linustechtips.com/news/nvidia-kills-off-gamestream-feature-on-shield-devices/)
*   [https://github.com/moonlight-stream/moonlight-docs/wiki/Frequently-Asked-Questions](https://github.com/moonlight-stream/moonlight-docs/wiki/Frequently-Asked-Questions)
*   [https://www.canyourunit.com/games/moonlight/](https://www.canyourunit.com/games/moonlight/)
*   [https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide](https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide)
*   [https://www.howtogeek.com/889650/it-seems-like-nvidia-killed-gamestream-to-funnel-more-customers-into-geforce-now/](https://www.howtogeek.com/889650/it-seems-like-nvidia-killed-gamestream-to-funnel-more-customers-into-geforce-now/)
*   [https://github.com/moonlight-stream/moonlight-docs/wiki/NVIDIA-GameStream-End-Of-Service-Announcement-FAQ](https://github.com/moonlight-stream/moonlight-docs/wiki/NVIDIA-GameStream-End-Of-Service-Announcement-FAQ)
*   [https://shattered.io/moonlight-vs-steam-link/](https://shattered.io/moonlight-vs-steam-link/)
*   [https://github.com/moonlight-stream/moonlight-docs/wiki/Troubleshooting](https://github.com/moonlight-stream/moonlight-docs/wiki/Troubleshooting)
*   [https://www.reddit.com/r/MoonlightStreaming/comments/1ax952p/ultimate_troubleshooting_guide_for_moonlight/](https://www.reddit.com/r/MoonlightStreaming/comments/1ax952p/ultimate_troubleshooting_guide_for_moonlight/)
*   [https://evezone.com/steam-link-vs-moonlight/](https://evezone.com/steam-link-vs-moonlight/)
*   [https://www.reddit.com/r/MoonlightStreaming/comments/1000m9r/steamlink_vs_moonlightsunshine_why/](https://www.reddit.com/r/MoonlightStreaming/comments/1000m9r/steamlink_vs_moonlightsunshine_why/)
*   [https://www.reddit.com/r/MoonlightStreaming/comments/1d1n03m/moonlightsunshine_optimisation_and_common_issues/](https://www.reddit.com/r/MoonlightStreaming/comments/1d1n03m/moonlightsunshine_optimisation_and_common_issues/)
*   [https://tinkr.com/moonlight-vs-parsec-vs-steam-link/](https://tinkr.com/moonlight-vs-parsec-vs-steam-link/)
*   [https://apps.apple.com/us/app/moonlight-game-streaming/id1000551566](https://apps.apple.com/us/app/moonlight-game-streaming/id1000551566)
*   [https://www.youtube.com/watch?v=1xN-6-q001Q](https://www.youtube.com/watch?v=1xN-6-q001Q)
*   [https://lizardbyte.dev/sunshine/](https://lizardbyte.dev/sunshine/)
*   [https://sourceforge.net/projects/sunshine-gamestream/](https://sourceforge.net/projects/sunshine-gamestream/)
*   [https://clore.ai/guides/gaming-streaming/sunshine-moonlight-remote-gaming](https://clore.ai/guides/gaming-streaming/sunshine-moonlight-remote-gaming)
*   [https://docs.lizardbyte.dev/projects/sunshine/en/latest/about/](https://docs.lizardbyte.dev/projects/sunshine/en/latest/about/)
*   [https://www.reddit.com/r/SBCGaming/comments/18k2123/awhile_ago_there_were_rumors_that_nvidia_was/](https://www.reddit.com/r/SBCGaming/comments/18k2123/awhile_ago_there_were_rumors_that_nvidia_was/)
*   [https://www.reddit.com/r/cloudygamer/comments/1000m9r/nvidia_gamestream_closure_alternatives/](https://www.reddit.com/r/cloudygamer/comments/1000m9r/nvidia_gamestream_closure_alternatives/)
*   [https://www.youtube.com/watch?v=HVuYQ8UQ9Yg](https://www.youtube.com/watch?v=HVuYQ8UQ9Yg)
*   [https://www.youtube.com/watch?v=J32mN40Rz9Y](https://www.youtube.com/watch?v=J32mN40Rz9Y)
*   [https://play.google.com/store/apps/details?id=com.limelight](https://play.google.com/store/apps/details?id=com.limelight)
*   [https://github.com/moonlight-stream/moonlight-docs/wiki/GameStream-Migration](https://github.com/moonlight-stream/moonlight-docs/wiki/GameStream-Migration)
*   [https://www.reddit.com/r/MoonlightStreaming/comments/16p8003/ultimate_guide_to_configuring_moonlight_sunshine/](https://www.reddit.com/r/MoonlightStreaming/comments/16p8003/ultimate_guide_to_configuring_moonlight_sunshine/)
*   [https://www.microsoft.com/en-us/p/moonlight-repacked/9p16g1g26210](https://www.microsoft.com/en-us/p/moonlight-repacked/9p16g1g26210)
*   [https://github.com/moonlight-stream](https://github.com/moonlight-stream)
*   [https://www.xda-developers.com/android-tv-box-moonlight-game-streaming/](https://www.xda-developers.com/android-tv-box-moonlight-game-streaming/)
*   [https://docs.lizardbyte.dev/projects/sunshine/en/latest/about/system_requirements.html](https://docs.lizardbyte.dev/projects/sunshine/en/latest/about/system_requirements.html)
*   [https://docs.lizardbyte.dev/projects/sunshine/en/latest/about/feature_compatibility.html](https://docs.lizardbyte.dev/projects/sunshine/en/latest/about/feature_compatibility.html)
*   [https://www.twingate.com/docs/sunshine-remote-game-streaming/](https://www.twingate.com/docs/sunshine-remote-game-streaming/)
*   [https://www.youtube.com/watch?v=HVuYQ8UQ9Yg](https://www.youtube.com/watch?v=HVuYQ8UQ9Yg)