import RedBook
import pandas as pd
import sqlite3
from datetime import datetime


database_name = 'Goals.db'

def minimum_effective_date(goals, days_behind):
    min_date = goals['Object'].apply(lambda x: min(x.effective_schedule_dates.values()))
    lag = (pd.to_datetime(datetime.now().date()) - min_date).dt.days
    return lag >= days_behind

def effective_date(goals, days_behind, schedule):
    min_date = goals['Object'].apply(lambda x: x.effective_schedule_dates[schedule])
    lag = (pd.to_datetime(datetime.now().date()) - min_date).dt.days
    return lag >= days_behind

#Percent Complete habit
def habit_completion(habits, completion):
    
    return habits['Object'].apply(lambda x: x.completion_percent) <= completion


def habit_streak(habits, streak):
    return habits['Object'].apply(lambda x: x.streak) <= streak

#Completed for this period

#Pick frequency

#Make one example where it is < x % complete with it not being complete this week

#Add a group select 

from datetime import datetime
with sqlite3.connect(database_name) as conn:
    #existing_progress = list(pd.read_sql("SELECT * FROM progress", conn)['Goal Name'].unique())
    #goals, work_log = RedBook.Data.process_goals_SQL(conn)
    #expected_progress_table, expected_work_table, percent_left_table, expected_work_tables = RedBook.Tables.build_expected_work_tables(goals)
    #RedBook.Data.filter_increment_hiding(goals, expected_work_tables)
    #print(RedBook.Data.check_table_exists(conn, 'groups'))
    #tables 
    goals, work_log = RedBook.Data.process_goals_SQL(conn)
    print(minimum_effective_date(goals, 11))
    print(effective_date(goals, 11, 'Historical'))
    
    habits, progress = RedBook.Data.process_habits_SQL(conn)
    
    
    print(habit_streak(habits, 2))
    print(habit_completion(habits, .2))
    
    
    #expected_progress_table = RedBook.Tables.build_expected_progress_table(goals)
    #expected_work_table = RedBook.Tables.build_expected_work_table(goals)
    
    #expected_progress_table, expected_work_table, expected_work_tables = RedBook.Tables.build_expected_work_tables(goals)

    
    #habits, progress = RedBook.Data.process_habits_SQL(conn)
    #a = RedBook.Tables.create_streak_tables(habits)
    #print(a)

    #print(pd.to_datetime(pl.index.get_level_values(0).astype(str), format='%Y') + \
    #         pd.to_timedelta((pl.index.get_level_values(1) * 7).astype(str) + ' days'))
    #print(create_progress_log3(a.progress_log2, "Weekly"))
    #table = RedBook.Tables.build_expected_progress_table_habits(habits)
    #["Daily","Weekly","Monthly","Quarterly","Yearly"]
    #tasks = RedBook.Data.pull_tasks_SQL(conn)

    #RedBook.Data.check_goal_completion(conn, goals)
    #tasks = RedBook.Data.pull_tasks_SQL(conn)
    