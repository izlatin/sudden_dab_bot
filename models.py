from database import get_database
from datetime import datetime

class Stats:
    def __init__(self, id: int, chat_id: int, user_id: int, dabs_count: int,
                 dabs_on_time_count: int, streak: int, max_streak: int) -> None:
        self.id = id
        self.chat_id = chat_id
        self.user_id = user_id
        self.dabs_count = dabs_count
        self.dabs_on_time_count = dabs_on_time_count
        self.streak = streak
        self.max_streak = max_streak
        
    def __repr__(self) -> str:
        return f"{self.user_id} in chat {self.chat_id}: {self.dabs_count} ({self.dabs_on_time_count}) with streak {self.streak} (max. {self.max_streak})"


class StatsTable:
    
    table_name = "stats"
    
    def __init__(self, chat_id: int, user_id: int, on_time: bool) -> None:
        self.chat_id = chat_id
        self.user_id = user_id
        self.on_time = on_time
        
        self.cursor, self.conn = get_database()
        self.id = None
    
    @classmethod 
    def create_table(cls):
        cursor, conn = get_database()
        
        sql = f"""
            CREATE TABLE IF NOT EXISTS {cls.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                dabs_count INTEGER,
                dabs_on_time_count INTEGER,
                streak INTEGER,
                max_streak INTEGER,
                UNIQUE(chat_id, user_id) ON CONFLICT IGNORE
            )
        """
        cursor.execute(sql)
        conn.commit()
    
    @classmethod
    def drop_table(cls):
        cursor, conn = get_database()
        
        sql = f"""   
            DROP TABLE IF EXISTS {cls.table_name};
        """
        cursor.execute(sql)
        conn.commit()
    
    @classmethod
    def if_exists(cls, chat_id, user_id) -> bool:
        cursor, _ = get_database()
        sql = f"""   
            SELECT id FROM {cls.table_name} WHERE chat_id={chat_id} AND user_id={user_id};
        """
        cursor.execute(sql)
        exists = bool(cursor.fetchall())
        return exists
    
    def save(self):
        if not self.if_exists(self.chat_id, self.user_id):
            default = int(self.on_time)
            sql = f"""
                INSERT INTO {self.table_name} (chat_id, user_id, dabs_count, dabs_on_time_count, streak, max_streak)
                VALUES ({self.chat_id}, {self.user_id}, 1, {default}, {default}, {default})
            """

            self.cursor.execute(sql)
            self.conn.commit()
            self.id = self.cursor.lastrowid
            return
        
        item = self.get(self.chat_id, self.user_id)
        
        dabs_count = item.dabs_count + 1
        dabs_on_time = item.dabs_on_time_count
        streak = item.streak
        max_streak = item.max_streak
        if self.on_time:
            dabs_on_time += 1
            streak += 1
            if streak > max_streak:
                max_streak = streak
        else:
            if streak > max_streak:
                max_streak = streak
            streak = 0
        
        sql = f"""
                UPDATE {self.table_name} 
                SET dabs_count={dabs_count}, dabs_on_time_count={dabs_on_time}, streak={streak}, max_streak={max_streak}
                WHERE id={item.id}
            """
        self.cursor.execute(sql)
        self.conn.commit()

    @classmethod
    def create(cls, chat_id, user_id, on_time):

        new_instance = cls(chat_id, user_id, on_time)
        new_instance.save()

        return cls.get_by_id(new_instance.id)
    
    @classmethod
    def get_by_id(cls, id) -> Stats:
        cursor, _ = get_database()
        
        sql = f"""
                SELECT * from {cls.table_name}
                WHERE id={id}
            """
        cursor.execute(sql)
        item = cursor.fetchone()
        if not item:
            return None
        item = list(item)
        return cls.row_to_stats(item)
    
    @classmethod
    def get(cls, chat_id, user_id) -> Stats:
        cursor, _ = get_database()
        
        sql = f"""
                SELECT * from {cls.table_name}
                WHERE chat_id={chat_id} AND user_id={user_id}
            """
        cursor.execute(sql)
        item = cursor.fetchone()
        if not item:
            return None
        item = list(item)
        return cls.row_to_stats(item)
    
    @classmethod
    def row_to_stats(cls, row) -> Stats:
        return Stats(
            id = row[0],
            chat_id=row[1],
            user_id=row[2],
            dabs_count=row[3],
            dabs_on_time_count=row[4],
            streak=row[5],
            max_streak=row[6]
        )
    
    @classmethod
    def get_chat_stats(cls, chat_id) -> list[Stats]:
        cursor, _ = get_database()
        
        sql = f"""
                SELECT * FROM {cls.table_name}
                WHERE chat_id={chat_id}
                ORDER BY streak DESC
            """
        
        rows = cursor.execute(sql).fetchall()
        return list(map(lambda x: cls.row_to_stats(x), rows))
    

class Session:
    def __init__(self, chat_id: int, next_dab: datetime = None, last_dab_msg_id: int = None,
                 last_dab_msg_time: datetime = None, active: bool = None) -> None:
        self.chat_id = chat_id
        self.next_dab = next_dab
        self.last_dab_msg_id = last_dab_msg_id
        self.last_dab_msg_time = last_dab_msg_time
        self.active = active
        
    def __repr__(self) -> str:
        active = "active"
        if not self.active:
            active = "inactive"
        return f"Chat {self.chat_id} ({active}), next dab on {self.next_dab}"


class SessionTable:
    
    table_name = "session"
    
    def __init__(self, chat_id: int, next_dab: datetime = None, last_dab_msg_id: int = None,
                 last_dab_msg_time: datetime = None, active: bool = None) -> None:
        self.chat_id = chat_id
        self.next_dab = next_dab
        self.last_dab_msg_id = last_dab_msg_id
        self.last_dab_msg_time = last_dab_msg_time
        self.active = active
        
        self.cursor, self.conn = get_database()
    
    @classmethod 
    def create_table(cls):
        cursor, conn = get_database()
        
        sql = f"""
            CREATE TABLE IF NOT EXISTS {cls.table_name} (
                chat_id INTEGER PRIMARY KEY,
                next_dab TIMESTAMP,
                last_dab_msg_id INTEGER,
                last_dab_msg_time TIMESTAMP,
                active INTEGER
            )
        """
        cursor.execute(sql)
        conn.commit()
    
    @classmethod
    def drop_table(cls):
        cursor, conn = get_database()
        
        sql = f"""   
            DROP TABLE IF EXISTS {cls.table_name};
        """
        cursor.execute(sql)
        conn.commit()
    
    @classmethod
    def if_exists(cls, chat_id) -> bool:
        cursor, _ = get_database()
        sql = f"""   
            SELECT chat_id FROM {cls.table_name} WHERE chat_id={chat_id};
        """
        cursor.execute(sql)
        exists = bool(cursor.fetchall())
        return exists
    
    def save(self):
        if not self.if_exists(self.chat_id):
            sql = f"""
                INSERT INTO {self.table_name} (chat_id)
                VALUES ({self.chat_id})
            """

            self.cursor.execute(sql)
            self.conn.commit()
            
        item = self.get(self.chat_id)
        next_dab = self.next_dab
        last_dab_msg_id = self.last_dab_msg_id
        last_dab_msg_time = self.last_dab_msg_time
        active = self.active
        
        if not next_dab:
            next_dab = item.next_dab
        if not last_dab_msg_id:
            last_dab_msg_id = item.last_dab_msg_id
        if not last_dab_msg_time:
            last_dab_msg_time = item.last_dab_msg_time
        if active == None and item.active != None:
            active = int(item.active)
        
        
        sql = f"""
                UPDATE {self.table_name} 
                SET next_dab=?, last_dab_msg_id=?, last_dab_msg_time=?, active=?
                WHERE chat_id={self.chat_id}
            """
            
        self.cursor.execute(sql, (next_dab, last_dab_msg_id, last_dab_msg_time, active))
        self.conn.commit()

    @classmethod
    def create(cls, chat_id: int, next_dab: datetime = None, last_dab_msg_id: int = None,
                 last_dab_msg_time: datetime = None, active: bool = None):

        new_instance = cls(chat_id, next_dab, last_dab_msg_id, last_dab_msg_time, active)
        new_instance.save()

        return cls.get(chat_id)
    
    @classmethod
    def get(cls, id) -> Session:
        cursor, _ = get_database()
        
        sql = f"""
                SELECT * from {cls.table_name}
                WHERE chat_id={id}
            """
        cursor.execute(sql)
        item = cursor.fetchone()
        if not item:
            return None
        item = list(item)
        return cls.row_to_sessions(item)
    
    @classmethod
    def row_to_sessions(cls, row) -> Session:
        return Session(
            chat_id=row[0],
            next_dab=row[1],
            last_dab_msg_id=row[2],
            last_dab_msg_time=row[3],
            active=bool(row[4])
        )

    @classmethod
    def get_active_sessions(cls) -> list[Session]:
        cursor, _ = get_database()
        
        sql = f"""
                SELECT * FROM {cls.table_name}
                WHERE active=1
            """
        
        rows = cursor.execute(sql).fetchall()
        return list(map(lambda x: cls.row_to_sessions(x), rows))