from database import init_database, table_exists
from models import StatsTable, SessionTable
from datetime import datetime


init_database([StatsTable, SessionTable])
# StatsTable.create(123, 1, True)
# StatsTable.create(123, 2, False)
# StatsTable.create(123, 3, True)
# StatsTable(123, 3, True).save()
# StatsTable.create(321, 444, False)

print(SessionTable.get_active_sessions())