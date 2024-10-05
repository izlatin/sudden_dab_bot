import sqlite3
import os


DATABASE_FILENAME = "db.sqlite3"
CURSOR = None
CONNECTION = None

def init_database(tables=[]):
    global CURSOR, CONNECTION

    if not os.path.exists(DATABASE_FILENAME):
        db = open(DATABASE_FILENAME, 'w')
        db.close()

    CONNECTION = sqlite3.connect(DATABASE_FILENAME,
                                detect_types=sqlite3.PARSE_DECLTYPES | 
                                sqlite3.PARSE_COLNAMES)
    CURSOR = CONNECTION.cursor()
    
    for table in tables:
        if not table_exists(table.table_name):
            table.create_table()
            print("Created table", table.table_name)
    
    print("Database initialized")


def table_exists(name):
    global CURSOR, CONNECTION
    
    sql = f"""
        SELECT name FROM sqlite_master WHERE type='table' AND name='{name}';
        """
    CURSOR.execute(sql)
    return bool(CURSOR.fetchall())
    
    
def close_database():
    global CURSOR, CONNECTION
    
    CONNECTION.close()
    CURSOR = None
    
    print("Database closed")

def get_database():
    return CURSOR, CONNECTION