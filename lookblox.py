import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
from datetime import datetime
from typing import List, Optional

TOKEN = "YOUR_DISCORD_BOT_TOKEN"
LOG_CHANNEL_ID = YOUR_ID_CHANNEL_LOG_ON_YOUR_DISCORD
GUILD_ID = YOUR_ID_SERVER_DISCORD
COOLDOWN_SECONDS = 10
CREDITS_TEXT = "Developed by Numerologue."

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def fetch_json(session: aiohttp.ClientSession, url: str, method: str = "GET", **kwargs):
    try:
        if method == "GET":
            async with session.get(url, **kwargs) as resp:
                if resp.status == 200:
                    return await resp.json()
        elif method == "POST":
            async with session.post(url, **kwargs) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception as e:
        print(f"[fetch_json] Error for {url}: {e}")
    return None

async def resolve_user(session: aiohttp.ClientSession, username: str) -> Optional[dict]:
    payload = {"usernames": [username], "excludeBannedUsers": False}
    data = await fetch_json(session, "https://users.roblox.com/v1/usernames/users", method="POST", json=payload)
    if not data or not data.get("data"):
        return None
    return data["data"][0]

def add_footer(embed: discord.Embed) -> discord.Embed:
    embed.set_footer(text=CREDITS_TEXT)
    return embed

class EmbedPaginator(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed]):
        super().__init__(timeout=180)
        self.embeds = embeds
        self.index = 0

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index - 1) % len(self.embeds)
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index + 1) % len(self.embeds)
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

@bot.tree.command(name="check", description="Check full Roblox account info (profile, social, groups, games, badges, limiteds & RAP, previous usernames)")
@app_commands.describe(username="Roblox username to investigate")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS, key=lambda i: i.user.id)
async def check(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    embeds: List[discord.Embed] = []

    async with aiohttp.ClientSession() as session:
        resolved = await resolve_user(session, username)
        if not resolved:
            await interaction.followup.send(f"❌ User **{username}** not found.", ephemeral=True)
            return

        user_id = resolved["id"]
        alias = resolved.get("name") or username
        display_name = resolved.get("displayName", alias)

        # Profile
        profile = await fetch_json(session, f"https://users.roblox.com/v1/users/{user_id}") or {}

        # Avatar
        thumb = await fetch_json(session, f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=420x420&format=Png&isCircular=false") or {}
        avatar_url = None
        try:
            avatar_url = (thumb.get("data") or [{}])[0].get("imageUrl")
        except Exception:
            avatar_url = None

        # Social
        friends_ct = await fetch_json(session, f"https://friends.roblox.com/v1/users/{user_id}/friends/count") or {}
        followers_ct = await fetch_json(session, f"https://friends.roblox.com/v1/users/{user_id}/followers/count") or {}
        following_ct = await fetch_json(session, f"https://friends.roblox.com/v1/users/{user_id}/followings/count") or {}

        # Groups
        groups_data = await fetch_json(session, f"https://groups.roblox.com/v2/users/{user_id}/groups/roles") or {}

        # Games created
        games_data = await fetch_json(session, f"https://games.roblox.com/v2/users/{user_id}/games?sortOrder=Asc&limit=10") or {}

        # Badges (functional)
        badges_data = await fetch_json(session, f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=10&sortOrder=Asc") or {}

        # Limited items & RAP
        rap_total = 0
        limited_lines: List[str] = []
        cursor = None
        loops = 0
        while loops < 5:  # up to ~500 items
            url = f"https://inventory.roblox.com/v1/users/{user_id}/assets/collectibles?sortOrder=Asc&limit=100" + (f"&cursor={cursor}" if cursor else "")
            col_data = await fetch_json(session, url) or {}
            for it in col_data.get("data", []):
                name = it.get("name", "Unknown")
                asset_id = it.get("assetId")
                rap = it.get("recentAveragePrice") or 0
                rap_total += rap
                if asset_id and len(limited_lines) < 15:
                    limited_lines.append(f"[{name}](https://www.roblox.com/catalog/{asset_id}) — RAP: {rap}")
            cursor = col_data.get("nextPageCursor")
            loops += 1
            if not cursor:
                break

        # Previous usernames
        prev_names_data = await fetch_json(session, f"https://users.roblox.com/v1/users/{user_id}/username-history?limit=25&sortOrder=Desc") or {}

        # ---------------- EMBEDS ----------------
        # Overview / Profile
        e_profile = discord.Embed(
            title=f"{display_name} 👤 ",
            description=f"**Alias:** `{alias}`\n[Open Roblox Profile](https://www.roblox.com/users/{user_id}/profile)",
            color=discord.Color.blurple(),
        )
        e_profile.add_field(name="User ID", value=str(user_id), inline=True)
        e_profile.add_field(name="Verified Badge", value=("✅" if profile.get("hasVerifiedBadge") else "❌"), inline=True)
        e_profile.add_field(name="Banned", value=("✅" if profile.get("isBanned") else "❌"), inline=True)
        e_profile.add_field(name="Friends", value=str(friends_ct.get("count", 0)), inline=True)
        e_profile.add_field(name="Followers", value=str(followers_ct.get("count", 0)), inline=True)
        e_profile.add_field(name="Following", value=str(following_ct.get("count", 0)), inline=True)
        created = (profile.get("created") or "N/A").split("T")[0]
        e_profile.add_field(name="Join Date", value=created, inline=True)
        desc = profile.get("description") or "No description."
        e_profile.add_field(name="Description", value=desc[:1024], inline=False)
        if avatar_url:
            e_profile.set_thumbnail(url=avatar_url)
        embeds.append(add_footer(e_profile))

        # Groups (name + hyperlink)
        e_groups = discord.Embed(title="Groups 🏛️", color=discord.Color.green())
        if groups_data.get("data"):
            lines = []
            for g in groups_data["data"]:
                gid = g["group"]["id"]
                gname = g["group"]["name"]
                lines.append(f"[{gname}](https://www.roblox.com/groups/{gid}) — Role: {g['role']['name']}")
            e_groups.description = "\n".join(lines[:15])
        else:
            e_groups.description = "No groups found."
        embeds.append(add_footer(e_groups))

        # Games
        e_games = discord.Embed(title="Created Games 🎮", color=discord.Color.orange())
        if games_data.get("data"):
            lines = []
            for game in games_data["data"]:
                # Prefer rootPlaceId when present for URL, fallback to id
                place_id = game.get("rootPlaceId") or game.get("id")
                gname = game.get("name", "Unnamed")
                visits = game.get("placeVisits", 0)
                created_game = (game.get("created") or "").split("T")[0] if game.get("created") else "N/A"
                lines.append(f"[{gname}](https://www.roblox.com/games/{place_id}) — Visits: {visits} • Created: {created_game}")
            e_games.description = "\n".join(lines[:10])
        else:
            e_games.description = "No games found."
        embeds.append(add_footer(e_games))

        # Badges (functional)
        e_badges = discord.Embed(title="Badges 🏅", color=discord.Color.gold())
        if badges_data.get("data"):
            for b in badges_data["data"][:10]:
                e_badges.add_field(name=b.get("name", "Unnamed Badge"), value=b.get("description", "No description"), inline=False)
        else:
            e_badges.description = "No badges found."
        embeds.append(add_footer(e_badges))

        # Limiteds & RAP
        e_rap = discord.Embed(title="Limited Items & RAP 💎", color=discord.Color.teal())
        if limited_lines:
            e_rap.add_field(name="Items (sample)", value="\n".join(limited_lines), inline=False)
        e_rap.add_field(name="Total RAP", value=str(rap_total), inline=False)
        embeds.append(add_footer(e_rap))

        # Previous usernames
        e_prev = discord.Embed(title="Previous Usernames 📜", color=discord.Color.purple())
        if prev_names_data.get("data"):
            names = [row.get("name", "?") for row in prev_names_data["data"]]
            e_prev.description = f"```\n{', '.join(names)}\n```"
        else:
            e_prev.description = "No previous usernames."
        embeds.append(add_footer(e_prev))

        # Send paginated embeds
        await interaction.followup.send(embed=embeds[0], view=EmbedPaginator(embeds))

        # ---------------- LOGS (Embed) ----------------
        roblox_profile_link = f"https://www.roblox.com/users/{user_id}/profile"
        log_embed = discord.Embed(title="🔍 Roblox Lookup Log", color=discord.Color.dark_blue(), timestamp=datetime.utcnow())
        log_embed.add_field(name="Discord User", value=f"{interaction.user.mention}\n`{interaction.user}` (ID: {interaction.user.id})", inline=False)
        log_embed.add_field(name="Roblox Username", value=f"[{alias}](" + roblox_profile_link + ")", inline=False)
        if avatar_url:
            log_embed.set_thumbnail(url=avatar_url)
        log_embed.set_footer(text="OSINT Bot Logs")

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        try:
            if log_channel is None:
                # Fallback to fetch if not cached
                log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)
            await log_channel.send(embed=log_embed)
        except Exception as e:
            print(f"[logs] Unable to send to log channel: {e}")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        guild = discord.Object(id=GUILD_ID)
        await bot.tree.sync(guild=guild)
        print("✅ Slash commands synced.")
    except Exception as e:
        print(f"❌ Sync error: {e}")

bot.run(TOKEN)

