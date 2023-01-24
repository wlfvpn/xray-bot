#!/usr/bin/env python

import logging
import requests
from telegram import __version__ as TG_VER
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
import yaml
from utils import load_config
import argparse
import datetime
import random
import asyncio

from link_manager import LinkManager
from utils import get_outline_key

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


async def instructions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="""Download the applications below and import the generated link.
                                                                          <b>Android:</b> Matsuri, V2rayNG
                                                                          <b>IOS:</b> NapsternetV, shadowrocket
                                                                          <b>Windows:</b> Neokoray, v2rayN
                                                                          <b>MacOS:</b> V2RayXS """, parse_mode="HTML")
    
async def gen_link(update: Update, context: ContextTypes.DEFAULT_TYPE, type):
    maintenance = await is_maintenance(update, context)
    if maintenance:
        return
    
    if not update.effective_user.username:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please setup a username for your telegram account.")
        return 
  
    if not await is_member(update, context, send_thank_you=False):
        return
    
    # lock = asyncio.Lock()
    # async with lock:
    if type == 'trojan':
        ret, urls = link_manager.get_link_trojan(str(update.effective_user.id),str(update.effective_user.username))
        logging.info(f'Trojan, Gave link to @{update.effective_user.username}')
    
    if type == 'vless':
        ret, urls = link_manager.get_link_vless(str(update.effective_user.id),str(update.effective_user.username))
        logging.info(f'VLESS, Gave link to @{update.effective_user.username}')

    if type == 'vmess':
        ret, urls = link_manager.get_link_vmess(str(update.effective_user.id),str(update.effective_user.username))
        logging.info(f'VMESS, Gave link to @{update.effective_user.username}')
    if ret:
        for (link_type, url) in urls.items():
            if url:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=link_type)

                text = "`" + '\n'.join(url) + "`"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="MarkdownV2")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=urls[0])

async def is_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    config = load_config(config_path)
    if config['maintenance']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry. The bot is under maintanance right now.")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=".در حال ارتقا ربات هستیم. ربات بصورت موقتی غیرفعال است.")
        # await context.bot.send_message(chat_id=update.effective_chat.id, text="در حال حاضر سرور پر شده است. ")

    return config['maintenance']

    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    maintenance = await is_maintenance(update, context)
    if maintenance:
        return
    
    if not await is_member(update,context):
        return
        
    keyboard = [[InlineKeyboardButton("VMess", callback_data="gen_vmess"),InlineKeyboardButton("VLESS", callback_data="gen_vless"),InlineKeyboardButton("Trojan", callback_data="gen_trojan")],
                [InlineKeyboardButton("گزارش استفاده", callback_data="usage")],
                [InlineKeyboardButton("Outline VPN گرفتن لینک", callback_data="gen_outline")],
                [InlineKeyboardButton("رو چه نرم افزاری کار میکنه؟", callback_data="instructions")],
                [InlineKeyboardButton("می خواهم کمک کنم",url="https://t.me/+0l8_7FaM-UkyNzIx", callback_data="contribute")],
                [InlineKeyboardButton("لینک کانال", url="https://t.me/WomanLifeFreedomVPN",callback_data="contact_support")],
                [InlineKeyboardButton("تست سرعت", web_app=WebAppInfo(url="https://pcmag.speedtestcustom.com"))]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose one of the following options:", reply_markup=reply_markup)
    
async def gen_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="هنوز این دکمه پیاده سازی نشده است.",)

async def gen_outline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="درحال برقراری ارتباط با سرور. لطفا چند دقیقه صبر کنید...")
    email = str(update.effective_user.id)+"@telegram.com"
    email = "test@test10"

    status, url = await get_outline_key(email)
    if status == 200:
        text = "`" + url + "`"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="MarkdownV2")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="حجم 4 گیگابایت. انقضا یک هفته."  )
        await context.bot.send_message(chat_id=update.effective_chat.id, text="برای اطلاعات بیشتر به  https://instagram.com/getoutlinevpnkey  مراجعه کنید."  )

    if status == 226:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="شما قبلا درخواست داده اید. لطفا یک هفته از درخواست قبلی صبر کنید.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    if query.data == "instructions":
        await instructions(update, context)
    elif query.data == "gen_trojan":
        await gen_link(update,context, 'trojan')
    elif query.data == "gen_vless":
        await gen_link(update,context, 'vless')
    elif query.data == "gen_vmess":
        await gen_link(update,context, 'vmess')

    elif query.data == "usage":
        await gen_report(update, context)
    elif query.data == "gen_outline":
        await gen_outline(update, context)  

async def is_member(update: Update, context: ContextTypes.DEFAULT_TYPE, send_thank_you=True):
    channel_id = '@WomanLifeFreedomVPN'  # The first argument is the channel ID
    user_id = update.effective_user.id # update.message.from_user.id  # Get the client's user ID
    chat_member = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
    if chat_member.status in ["member", "creator"]:
        if send_thank_you:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you for subscribing to our channel!")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Please subscribe to our channel {channel_id}.")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="لطفا ابتدا عضو کانال شوید. این وی پی ان محدود به اعضای کانال می باشد.")
    return chat_member.status in ["member", "creator"]

def main() -> None:
    # Parse the config file path from the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path', help='Path to the config file', default='config.yaml')
    args = parser.parse_args()
    global config_path
    config_path = args.config_path

    # Load the config file
    config = load_config(config_path)    
      
    global link_manager
    link_manager = LinkManager(config)

    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config['telegram_bot_token']).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

