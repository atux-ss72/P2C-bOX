# P2C-bOX (Peer-to-Peer Chat Box)

P2C-bOX is a peer-to-peer chat application designed to establish direct communication between clients without requiring a dedicated chat server. The tool leverages Cloudflare Tunnel (cloudflared) to generate a secure public link, enabling users to connect and communicate easily.

Messages are exchanged directly between connected clients, reducing dependence on centralized infrastructure and providing greater privacy for conversations.

*Features
🔗 Peer-to-Peer Communication – Direct messaging between connected clients.
🌐 Cloudflared Integration – Automatically generates a public connection link.
🚫 No Dedicated Chat Server Required – No need to deploy or maintain a chat server.
🔒 Privacy-Focused Design – Conversations are not stored on a centralized chat server.
⚡ Lightweight and Easy to Use – Quick setup with minimal configuration.
Included Utilities
Free_Port

Free_Port is a utility tool included with the project that automatically identifies and releases processes occupying a specified network port. This allows developers to quickly reuse ports without manually locating and terminating conflicting applications.

Features
🔍 Detects processes using a specific port.
⚡ Frees occupied ports automatically.
🛠 Useful during development and testing.
🚀 Eliminates manual process termination steps.
How P2C-bOX Works
1.Start P2C-bOX.
2.Cloudflared random generates a public connection link.
3.Share the generated link with another user.
4.The recipient connects using the link.
5.A direct communication channel is established between both clients.

*Project Goal

P2C-bOX aims to provide a simple, lightweight, and privacy-oriented communication platform that minimizes reliance on centralized infrastructure while remaining easy to deploy and use.
