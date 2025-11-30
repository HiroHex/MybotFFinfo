import telebot
import requests
import time
from datetime import datetime

BOT_TOKEN = "8244684898:AAGr1USCJMT_x8L0NzleqA0BmJ4vfILO4WU"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

ALLOWED_GROUPS = "-1003038685431"

API_LINK = "https://info-hexv-3.vercel.app/"

def format_timestamp(timestamp):
    """Convert timestamp to readable date"""
    try:
        return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "N/A"

def decode_unicode_escape(text):
    """Decode unicode escape sequences like \\u0417 to actual characters"""
    try:
        return text.encode('utf-8').decode('unicode_escape')
    except:
        return text

@bot.message_handler(commands=["inf"])
def handle_info(message):
    if str(message.chat.id) not in ALLOWED_GROUPS:
        return

    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "<b>Usage: /inf {uid}</b>\n\n<b>Example:</b> <code>/inf 9042676924</code>")
        return

    uid = args[1]
    
    # Validate UID contains only numbers
    if not uid.isdigit():
        bot.reply_to(message, "<b>Error:</b> UID must contain only numbers")
        return

    processing_msg = bot.reply_to(message, "<b>Fetching player info...</b>")
    try:
        # Always use SG region
        url = f"{API_LINK}/info?uid={uid}"
        response = requests.get(url, timeout=15)
        
        if response and response.status_code == 200:
            result = response.json()
            
            # Extract information from the new structure
            account_info = result.get("AccountInfo", {})
            profile_info = result.get("AccountProfileInfo", {})
            guild_info = result.get("GuildInfo", {})
            credit_score_info = result.get("creditScoreInfo", {})
            pet_info = result.get("petInfo", {})
            social_info = result.get("socialinfo", {})
            
            # Format account information
            account_name = account_info.get('AccountName', 'N/A')
            # Decode unicode escape sequences
            account_name = decode_unicode_escape(account_name)
            # Escape HTML characters
            account_name = account_name.replace('<', '&lt;').replace('>', '&gt;')
            
            # Format signature with proper decoding
            signature = social_info.get('signature', 'N/A')
            signature = decode_unicode_escape(signature)
            signature = signature.replace('<', '&lt;').replace('>', '&gt;')
            
            # Format guild information
            guild_text = ""
            guild_name = guild_info.get('GuildName')
            if guild_name:
                guild_text = (
                    f"<b>👥 Guild:</b> {guild_name}\n"
                    f"<b>🆔 Guild ID:</b> {guild_info.get('GuildID', 'N/A')}\n"
                    f"<b>📈 Guild Level:</b> {guild_info.get('GuildLevel', 'N/A')}\n"
                    f"<b>👥 Members:</b> {guild_info.get('GuildMember', 'N/A')}/{guild_info.get('GuildCapacity', 'N/A')}\n"
                    f"<b>👑 Owner:</b> {guild_info.get('GuildOwner', 'N/A')}\n"
                )
            else:
                guild_text = "<b>👥 Guild:</b> No guild\n"
            
            # Format profile information (только количество, без ID предметов)
            profile_text = ""
            if profile_info:
                outfits_count = len(profile_info.get('EquippedOutfit', []))
                skills_count = len(profile_info.get('EquippedSkills', []))
                profile_text = (
                    f"<b>👕 Equipped Outfits:</b> {outfits_count} items\n"
                    f"<b>🎒 Equipped Skills:</b> {skills_count} skills\n"
                )
            
            # Format pet information
            pet_text = ""
            if pet_info:
                pet_text = (
                    f"<b>🐾 Pet Level:</b> {pet_info.get('level', 'N/A')}\n"
                    f"<b>⭐ Pet EXP:</b> {pet_info.get('exp', 'N/A')}\n"
                    f"<b>🎨 Pet Skin:</b> {pet_info.get('skinId', 'N/A')}\n"
                    f"<b>🔮 Pet Skill:</b> {pet_info.get('selectedSkillId', 'N/A')}\n"
                    f"<b>✅ Pet Selected:</b> {pet_info.get('isSelected', 'N/A')}\n"
                )
            else:
                pet_text = "<b>🐾 Pet:</b> No pet\n"
            
            # Format social information
            social_text = ""
            if social_info:
                language = social_info.get('language', 'N/A').replace('Language_', '')
                mode_prefer = social_info.get('modePrefer', 'N/A').replace('ModePrefer_', '')
                rank_show = social_info.get('rankShow', 'N/A').replace('RankShow_', '')
                time_active = social_info.get('timeActive', 'N/A').replace('TimeActive_', '')
                time_online = social_info.get('timeOnline', 'N/A').replace('TimeOnline_', '')
                
                social_text = (
                    f"<b>💬 Signature:</b>\n{signature}\n\n"
                    f"<b>🗣️ Language:</b> {language}\n"
                    f"<b>🎮 Preferred Mode:</b> {mode_prefer}\n"
                    f"<b>📊 Rank Display:</b> {rank_show}\n"
                    f"<b>⏰ Active Time:</b> {time_active}\n"
                    f"<b>📅 Online Time:</b> {time_online}\n"
                )
            
            # Format equipped weapons (только количество, без ID)
            weapons_text = ""
            weapons_count = len(account_info.get('EquippedWeapon', []))
            if weapons_count > 0:
                weapons_text = f"<b>🔫 Equipped Weapons:</b> {weapons_count} items\n"
            else:
                weapons_text = "<b>🔫 Equipped Weapons:</b> None\n"
            
            # Compile final message
            text = (
                "<b>🎮 PLAYER INFORMATION</b>\n\n"
                f"<b>👤 Basic Info:</b>\n"
                f"<b>   Name:</b> {account_name}\n"
                f"<b>   🆔 UID:</b> {uid}\n"
                f"<b>   🌍 Region:</b> {account_info.get('AccountRegion', 'N/A')}\n"
                f"<b>   ⭐ Level:</b> {account_info.get('AccountLevel', 'N/A')}\n"
                f"<b>   📊 EXP:</b> {account_info.get('AccountEXP', 'N/A')}\n"
                f"<b>   👤 Avatar:</b> {account_info.get('AccountAvatarId', 'N/A')}\n"
                f"<b>   🎌 Banner:</b> {account_info.get('AccountBannerId', 'N/A')}\n"
                f"<b>   ❤️ Likes:</b> {account_info.get('AccountLikes', 'N/A')}\n"
                f"<b>   🎯 Badge:</b> {account_info.get('AccountBPID', 'N/A')} (Count: {account_info.get('AccountBPBadges', 'N/A')})\n"
                f"<b>   📅 Season:</b> {account_info.get('AccountSeasonId', 'N/A')}\n"
                f"<b>   🎮 Version:</b> {account_info.get('ReleaseVersion', 'N/A')}\n"
                f"<b>   🏷️ Title:</b> {account_info.get('Title', 'N/A')}\n"
                f"<b>   🅰️ Account Type:</b> {account_info.get('AccountType', 'N/A')}\n"
                f"<b>   🕒 Last Login:</b> {format_timestamp(account_info.get('AccountLastLogin', 'N/A'))}\n"
                f"<b>   📅 Created:</b> {format_timestamp(account_info.get('AccountCreateTime', 'N/A'))}\n\n"
                
                f"<b>🏆 Rank Info:</b>\n"
                f"<b>   BR Rank:</b> {account_info.get('BrRankPoint', 'N/A')} (Max: {account_info.get('BrMaxRank', 'N/A')})\n"
                f"<b>   CS Rank:</b> {account_info.get('CsRankPoint', 'N/A')} (Max: {account_info.get('CsMaxRank', 'N/A')})\n"
                f"<b>   Show BR Rank:</b> {account_info.get('ShowBrRank', 'N/A')}\n"
                f"<b>   Show CS Rank:</b> {account_info.get('ShowCsRank', 'N/A')}\n\n"
                
                f"{weapons_text}\n"
                
                f"<b>🎭 Profile Info:</b>\n{profile_text}\n"
                
                f"<b>👥 Guild Info:</b>\n{guild_text}\n"
                
                f"<b>🐾 Pet Info:</b>\n{pet_text}\n"
                
                f"<b>💬 Social Info:</b>\n{social_text}\n"
                
                f"<b>💰 Credit Score:</b> {credit_score_info.get('creditScore', 'N/A')}\n"
                f"<b>🎁 Reward State:</b> {credit_score_info.get('rewardState', 'N/A').replace('REWARD_STATE_', '')}\n"
            )
                
        else:
            text = "<b>❌ Failed to fetch player information. Please check the UID and try again.</b>"
        
        bot.edit_message_text(text, message.chat.id, processing_msg.message_id)
    except Exception as e:
        error_text = f"<b>❌ Error:</b> {str(e).replace('<', '&lt;').replace('>', '&gt;')}"
        bot.edit_message_text(error_text, message.chat.id, processing_msg.message_id)

# Удаляем вебхук перед запуском поллинга
try:
    bot.remove_webhook()
    time.sleep(1)
except Exception as e:
    print(f"Error removing webhook: {e}")

print("Bot running...")
bot.infinity_polling()