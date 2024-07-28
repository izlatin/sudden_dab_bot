import json
import logging
from random import randint, choice
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

MIN_TIME = datetime.strptime("10:00:00", "%H:%M:%S").time()
MAX_TIME = datetime.strptime("23:59:59", "%H:%M:%S").time()
INTERVAL = timedelta(days=2)
MIN_DISTANCE = timedelta(seconds=60 * 30)

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

def get_next_day():
    today = datetime.today()
    full_day_in_minutes = MAX_TIME.hour * 60 + MAX_TIME.minute - (MIN_TIME.hour * 60 + MIN_TIME.minute)
    today_minutes_left = MAX_TIME.hour * 60 + MAX_TIME.minute - (today.hour * 60 + today.minute)
    today_minutes_left = max(0, today_minutes_left - MIN_DISTANCE.seconds // 60)
    
    next_day = choice([0] * today_minutes_left + [1] * full_day_in_minutes + [2] * full_day_in_minutes)
    return next_day

def choose_next_dab_time():
    # chooses a proper time for the next dab randomly
    today = datetime.today()
    next_day = get_next_day()
    
    if next_day == 0:
        start_date = datetime.combine((today + timedelta(days=next_day)).date(), (today + MIN_DISTANCE).time())
    else:
        start_date = datetime.combine((today + timedelta(days=next_day)).date(), MIN_TIME)
    end_date = datetime.combine((today + timedelta(days=next_day)).date(), MAX_TIME)

    seconds = randint(0, int((end_date - start_date).total_seconds()))
    next_date = start_date + timedelta(seconds=seconds)

    due = (next_date - today).total_seconds()
    print(due, next_date)
    return due

