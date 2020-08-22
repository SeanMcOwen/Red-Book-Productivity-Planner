import pandas as pd
from RedBook.Classes.Goal import Goal

    
def pull_goals_data_SQL(conn):
    df = pd.read_sql("SELECT * FROM goals", conn)
    df['Start Date'] = pd.to_datetime(df['Start Date'])
    df['End Date'] = pd.to_datetime(df['End Date'])
    df = df[df['Progress Type'].isin(['Progress', 'Add'])]
    return df

def pull_work_log_SQL(goals, conn):
    work_log = pd.read_sql("SELECT * FROM progress", conn).pivot("Date", "Goal Name", "Value")
    work_log.index = pd.to_datetime(work_log.index)
    for col in work_log.columns:
        progress_type = goals[goals['Progress Name'] == col]['Progress Type'].iloc[0]
        #progress_type = goals.set_index('Goal Name')['Progress Type'].loc[col]
        units = goals[goals['Progress Name'] == col]['Units'].iloc[0]
        if progress_type == "Add":
            work_log[col] = work_log[col].fillna(0).cumsum()
        elif progress_type == "Progress":
            work_log[col] = work_log[col].fillna(method='ffill')
        work_log[col] = work_log[col] / units
    return work_log

def process_goals_SQL(conn):
    goals = pull_goals_data_SQL(conn)
    work_log = pull_work_log_SQL(goals, conn)
    goals = goals[goals['Completed'] != "Completed"]
    def apply_function(x):
        if x['Progress Name'] in work_log.columns:
            wl = work_log[x['Progress Name']]
        else:
            wl = None
        return Goal(x.to_dict(), wl)
    goals['Object'] = goals.apply(apply_function, axis=1)
    return goals, work_log