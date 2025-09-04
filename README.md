# 🔍 Roblox OSINT Discord Bot

A Discord bot for performing **OSINT (Open Source Intelligence)** on Roblox accounts.  
With a single slash command, it gathers and displays detailed information in paginated embeds :  

- Profile information (alias, ID, description, join date, verification, ban status…) 👤
- Groups and associated roles 🏛️
- Created games 🎮
- Account badges 🏅
- Limited items and total RAP (Recent Average Price) 💎
- Previous usernames 📜

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
git clone https://github.com/numerologue/LookBlox.git
cd LookBlox
```

### 2. Install dependencies

This bot requires Python 3.9+ and the following libraries :
```bash
pip install -r requirements.txt
```

Example `requirements.txt` :
```bash
discord.py
aiohttp
```

### 3. Configure the bot

In the bot's Python file, replace these constants with your own values :
```python
TOKEN = "YOUR_DISCORD_BOT_TOKEN"
LOG_CHANNEL_ID = YOUR_ID_CHANNEL_LOG_ON_YOUR_DISCORD
GUILD_ID = YOUR_ID_SERVER_DISCORD
```

👉 Security tip :
Never commit your token in plain text to a public repository.
Instead, use environment variables :
```bash
export DISCORD_TOKEN="your_token"
```

And in your Python code :
```python
import os
TOKEN = os.getenv("DISCORD_TOKEN")
```

## ▶️ Run the bot
```bash
python name_file.py
```

## 📜 Usage

In your Discord server (after inviting the bot with the correct permissions) :
```bash
/check username
```
The bot will return several paginated embeds with detailed Roblox OSINT data.

## 📸 Preview

Demo : https://youtu.be/ZPEaFz3lzvc

## 🛡️ Disclaimer

This bot is intended for educational and personal use only.
OSINT should always be conducted ethically and in compliance with platform rules.
The author takes no responsibility for misuse.

## 👨‍💻 Author

Developed by Numerologue. 
