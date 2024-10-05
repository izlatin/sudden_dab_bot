from database import init_database, table_exists
from models import StatsTable, Stats


init_database([StatsTable])
# StatsTable.create(123, 1, True)
# StatsTable.create(123, 2, False)
# StatsTable.create(123, 3, True)
# StatsTable(123, 3, True).save()
# StatsTable.create(321, 444, False)

print(StatsTable.get_chat_stats(123))