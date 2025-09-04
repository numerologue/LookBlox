# LookBlox
OSINT Discord Bot to find more information about a Roblox account.

# 🔍 Roblox OSINT Discord Bot

A Discord bot for performing **OSINT (Open Source Intelligence)** on Roblox accounts.  
With a single slash command, it gathers and displays detailed information in paginated embeds:  

- 👤 Profile information (alias, ID, description, join date, verification, ban status…)  
- 🏛️ Groups and associated roles  
- 🎮 Created games  
- 🏅 Account badges  
- 💎 Limited items and total RAP (Recent Average Price)  
- 📜 Previous usernames  

All lookups are logged automatically in a dedicated Discord channel.

---

## ⚙️ Features
- `/check <username>` slash command to investigate a Roblox account  
- Paginated embeds for easy navigation  
- **Cooldown system** to prevent spam  
- Automatic lookup logs sent to a chosen Discord channel  
- Author credits added in embed footers  

---

## 🚀 Installation

### 1. Clone the project
```bash
git clone https://github.com/your-username/roblox-osint-bot.git
cd roblox-osint-bot
