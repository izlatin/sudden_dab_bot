import json
import logging
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

def choose_next_dab_time():
    # chooses a proper time for the next dab randomly
    return 10

async def schedule_dab(chat_id, context: ContextTypes.DEFAULT_TYPE):
    due = choose_next_dab_time()

    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(sudden_dab, due, chat_id=chat_id, name=str(chat_id), data=due)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Мама не жди меня ночью, флеш мне в очко")
    await schedule_dab(update.effective_message.chat_id, context)
    

async def sudden_dab(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the sudden dab message."""
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"ВНЕЗАПНЫЙ ДЭБ!")
    await schedule_dab(job.chat_id, context)


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
    
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(stop_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()