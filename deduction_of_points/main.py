# import schedule
# import time
# from pytz import timezone
# from datetime import datetime, timedelta
#
#
# def job():
#
#     print("Выполняется каждые 24 часа в 00:00 по Московскому времени")
#
#
# moscow_tz = timezone('Europe/Moscow')
#
#
# def convert_to_moscow_time(dt):
#     return dt.astimezone(moscow_tz)
#
#
# current_time = datetime.now(tz=moscow_tz)
# next_run_time = current_time.replace(hour=0, minute=0, second=0) + timedelta(days=1)
# time_to_wait = (next_run_time - current_time).total_seconds()
# time.sleep(time_to_wait)
# job()
# schedule.every(24).hours.do(job)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)

from database import Database
import schedule
import time


def job():
    db = Database('../cfg/database')
    db.update_user_balances()
    print("Выполняется каждые 30 секунд")


schedule.every(10).seconds.do(job)


while True:
    schedule.run_pending()
    time.sleep(1)
