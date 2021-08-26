import datetime

clock_in_half_hour = datetime.datetime(year = 2021, month=8, day=25, hour=19, minute=22, second=51) + datetime.timedelta(minutes=30)
print(clock_in_half_hour)