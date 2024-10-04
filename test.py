from database import init_databse
from models import StatsTable, Stats


init_databse()
s = StatsTable(123, 789, 1)
s.save()
