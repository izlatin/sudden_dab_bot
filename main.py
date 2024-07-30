import json
import logging
from random import randint, choice
from datetime import datetime, timedelta, UTC
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

MIN_TIME = datetime.strptime("10:00:00", "%H:%M:%S").time()
MAX_TIME = datetime.strptime("23:59:59", "%H:%M:%S").time()
MIN_DISTANCE = timedelta(seconds=60 * 30)
DAB_REACTION_INTERVAL = timedelta(seconds=60 * 3)

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

def get_next_day():
    today = datetime.today()
    full_day_in_minutes = MAX_TIME.hour * 60 + MAX_TIME.minute - (MIN_TIME.hour * 60 + MIN_TIME.minute)
    if today.time() < MIN_TIME:
        today_minutes_left = full_day_in_minutes
    else:
        today_minutes_left = MAX_TIME.hour * 60 + MAX_TIME.minute - (today.hour * 60 + today.minute)
        today_minutes_left = max(0, today_minutes_left - MIN_DISTANCE.seconds // 60)
    
    next_day = choice([0] * today_minutes_left + [1] * full_day_in_minutes + [2] * full_day_in_minutes)
    return next_day

def choose_next_dab_time():
    # chooses a proper time for the next dab randomly
    today = datetime.today()
    next_day = get_next_day()
    
    if next_day == 0:
        start_date = datetime.combine(today.date(), max((today + MIN_DISTANCE).time(), MIN_TIME))
    else:
        start_date = datetime.combine((today + timedelta(days=next_day)).date(), MIN_TIME)
    end_date = datetime.combine((today + timedelta(days=next_day)).date(), MAX_TIME)

    seconds = randint(0, int((end_date - start_date).total_seconds()))
    next_date = start_date + timedelta(seconds=seconds)

    due = (next_date - today).total_seconds()
    print(due, next_date)
    return due


async def schedule_dab(chat_id, context: ContextTypes.DEFAULT_TYPE):
    due = choose_next_dab_time()

    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(sudden_dab, due, chat_id=chat_id, name=str(chat_id), data=due)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вы подписались на неслыханное веселье! " +
                                   "На каждый внезапный дэб вам нужно будет в течение 3 минут записать ответный кружочек с вашим дэбом. \n" +
                                   "Ну что ж...")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Мама не жди меня ночью, флеш мне в очко")
    await schedule_dab(update.effective_message.chat_id, context)
    

async def sudden_dab(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the sudden dab message."""
    job = context.job
    response = await context.bot.send_message(job.chat_id, text=f"!ВНЕЗАПНЫЙ ДЭБ!")
    context.chat_data["dab_message_id"] = response.id
    context.chat_data["dab_message_date"] = response.date
    await schedule_dab(job.chat_id, context)

async def dab_react(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send reaction if dab was sent on time"""
    if "dab_message_id" not in context.chat_data or "dab_message_date" not in context.chat_data:
        return
    
    dab_message_id = context.chat_data["dab_message_id"]
    dab_message_date = context.chat_data["dab_message_date"]
    reply_time = datetime.now(UTC) - dab_message_date
    if dab_message_id != update.effective_message.reply_to_message.id or reply_time > DAB_REACTION_INTERVAL:
        return

    await context.bot.set_message_reaction(update.effective_message.chat_id, update.effective_message.id, "🏆", is_big=True)
    

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Чао какао ай гесс")
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Ya vas ne ponyav")

if __name__ == '__main__':
    token = json.load(open("token.json", encoding='utf-8'))
    application = ApplicationBuilder().token(token["token"]).build()
    
    start_handler = CommandHandler('start', start)
    stop_handler = CommandHandler('stop', stop)
    dab_react_handler = MessageHandler(filters.REPLY & filters.VIDEO_NOTE, dab_react)
    
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(stop_handler)
    application.add_handler(dab_react_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()