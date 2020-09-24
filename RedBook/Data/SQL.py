import pandas as pd
from RedBook.Classes.Goal import Goal
from RedBook.Classes.Habit import Habit
from datetime import datetime

    
def pull_goals_data_SQL(conn):
    df = pd.read_sql("SELECT * FROM goals", conn)
    df['Start Date'] = pd.to_datetime(df['Start Date'])
    df['End Date'] = pd.to_datetime(df['End Date'])
    return df

def pull_work_log_SQL(goals, conn):
    work_log = pd.read_sql("SELECT * FROM progress", conn).pivot("Date", "Goal Name", "Value")
    work_log.index = pd.to_datetime(work_log.index)
    
    params = pd.read_sql("SELECT * FROM progress_params", conn).set_index("Goal Name")
    for col in work_log.columns:
        progress_type = params.loc[col, 'Progress Type']
        units  = params.loc[col, 'Units']
        if progress_type == "Add":
            work_log[col] = work_log[col].fillna(0).cumsum()
        elif progress_type == "Progress":
            work_log[col] = work_log[col].fillna(method='ffill')
        work_log[col] = work_log[col] / units

    return work_log, params

def process_goals_SQL(conn):
    goals = pull_goals_data_SQL(conn)
    work_log, params = pull_work_log_SQL(goals, conn)
    goals = goals[goals['Completed'] != "Completed"]
    goals = goals[goals['Start Date'] <= datetime.now()]
    def apply_function(x):
        wl = work_log[x['Progress Name']]
        x = x.to_dict()
        x['Progress Type'] = params.loc[x['Progress Name'], 'Progress Type']
        x['Units'] = params.loc[x['Progress Name'], 'Units']
        
        return Goal(x, wl)
    goals['Object'] = goals.apply(apply_function, axis=1)
    goals['Start Progress'] = goals['Object'].apply(lambda x: x.start_progress)
    return goals, work_log


def pull_habits_data_SQL(conn):
    df = pd.read_sql("SELECT * FROM habits", conn)
    df['Start Date'] = pd.to_datetime(df['Start Date'])
    return df


def pull_habits_log_SQL(conn):
    work_log = pd.read_sql("SELECT * FROM habits_progress", conn).pivot("Date", "Habit Name", "Progress")
    work_log.index = pd.to_datetime(work_log.index)
    return work_log

def pull_tasks_SQL(conn):
    tasks = pd.read_sql("SELECT * FROM tasks", conn)
    tasks['Due Date'] = pd.to_datetime(tasks['Due Date'])
    today = pd.to_datetime(datetime.now().date())
    week = today + pd.Timedelta("{}D".format(6-today.weekday()))
    tasks['Today'] = tasks['Due Date'] <= today
    tasks['Week'] = tasks['Due Date'] <= week
    
    month = (today.month % 12) + 1
    if today.month == 12:
        year = today.year + 1
    else:
        year = today.year + 1
    month = datetime(year, month, 1) - pd.Timedelta("1D")
    tasks['Month'] = tasks['Due Date'] <= week
    
    month = today.month
    if today.month == 10:
        year = today.year + 1
        month = 1
    else:
        year = today.year
        month = month + 3
    quarter = datetime(year, month, 1) - pd.Timedelta("1D")
    tasks['Quarter'] = tasks['Due Date'] <= quarter
    
    year = datetime(today.year+1, 1, 1) - pd.Timedelta("1D")
    tasks['Year'] = tasks['Due Date'] <= year
    return tasks

def process_habits_SQL(conn):
    habits = pull_habits_data_SQL(conn)
    work_log = pull_habits_log_SQL(conn)
    habits = habits[habits['Completed'] != "Completed"]
    habits = habits[habits['Start Date'] <= datetime.now()]
    def apply_function(x):
        wl = work_log[x['Habit Name']]
        x = x.to_dict()
        
        return Habit(x, wl)
    habits['Object'] = habits.apply(apply_function, axis=1)
    return habits, work_log