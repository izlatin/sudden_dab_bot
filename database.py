import sqlite3
import os


DATABASE_FILENAME = "db.sqlite3"
CURSOR = None
CONNECTION = None
TABLES = [
    
]

def init_databse():
    global CURSOR, CONNECTION

    if not os.path.exists(DATABASE_FILENAME):
        db = open(DATABASE_FILENAME, 'w')
        db.close()

    CONNECTION = sqlite3.connect(DATABASE_FILENAME)
    CURSOR = CONNECTION.cursor()
    
def close_database():
    global CURSOR, CONNECTION
    
    CONNECTION.close()
    CURSOR = None

def get_database():
    return CURSOR, CONNECTION