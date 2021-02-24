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
    goals['Object'] = ""
    goals['Start Progress'] = ""
    
    #Bump forward due date
    goals['End Date'] = goals['End Date'].apply(lambda x: max(x, pd.to_datetime(datetime.now().date())))
    
    def apply_function(x):
        wl = work_log[x['Progress Name']]
        x = x.to_dict()
        x['Progress Type'] = params.loc[x['Progress Name'], 'Progress Type']
        x['Units'] = params.loc[x['Progress Name'], 'Units']
        
        return Goal(x, wl)
    if len(goals) > 0:
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

def pull_tasks_SQL(conn, filter_complete=True):
    tasks = pd.read_sql("SELECT * FROM tasks", conn)
    if filter_complete:
        tasks = tasks[tasks['Completed'] != 'Completed']
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
    tasks['Month'] = tasks['Due Date'] <= month
    
    month = 1+(today.quarter-1)*3
    if month == 10:
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

def check_goal_completion(conn, goals):
    complete = goals.set_index("Goal Name")['Object'].apply(lambda goal: abs(goal.current_progress - goal.start_progress) / abs(goal.end_progress - goal.start_progress))
    complete = (complete >= 1)
    complete = complete[complete]
    for goal in complete.index:
        conn.cursor().execute("UPDATE goals SET Completed = 'Completed' WHERE `Goal Name` = '{}'".format(goal))
        conn.commit()
        
        df = pd.read_sql("SELECT * FROM goals", conn)
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        df['End Date'] = pd.to_datetime(df['End Date'])
        df.to_csv("Goals.csv", index=False)
        
        
        completed = pd.DataFrame([[goal, "Goal", pd.to_datetime(datetime.today().date())]],
                                 columns = ['Name', 'Type', 'Date'])
        completed.to_sql("Completed", conn, if_exists='append', index=False)
        df = pd.read_sql("SELECT * FROM Completed", conn)
        df['Date'] = pd.to_datetime(df['Date'])
        df.to_csv("Completed.csv", index=False)
        
def check_table_exists(conn, name):
    curr = conn.cursor()
    tables = curr.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    tables = [x[0] for x in tables]
    return name in tables

def filter_increment_hiding(goals, tables):
    for key in tables.keys():
        table = tables[key]
        table = table[goals.set_index("Goal Name")[key].reindex(table.index).astype(bool)]
        tables[key] = table
    
