import sqlite3
import pandas as pd
import os

def excel_to_db(conn):
    if 'Goals.csv' in os.listdir("."):
        goals = pd.read_csv("Goals.csv")
        goals.to_sql("goals", conn, if_exists='replace', index=False)
    if "project_log.csv" in os.listdir("."):
        progress = pd.read_csv("project_log.csv", index_col=0)
        progress.index = pd.to_datetime(progress.index)
        progress = progress.stack().reset_index()
        progress.columns = ['Date', 'Goal Name', 'Value']
        progress.to_sql("progress", conn, if_exists='replace', index=False)
    if "Group.csv" in os.listdir("."):
        group = pd.read_csv("Group.csv", index_col=0)
        group.to_sql("groups", conn, if_exists='replace', index=False)
    if "progress_params.csv" in os.listdir("."):
        param = pd.read_csv("progress_params.csv", index_col=0)
        param.to_sql("progress_params", conn, if_exists='replace', index=False)
    if "Habits.csv" in os.listdir("."):
        habits = pd.read_csv("Habits.csv", index_col=0)
        habits.to_sql("habits", conn, if_exists='replace', index=False)
        
        habits = pd.read_csv("Habits Progress.csv", index_col=0)
        habits['Date'] = pd.to_datetime(habits['Date'])
        habits.to_sql("habits_progress", conn, if_exists='replace', index=False)
    if "Tasks.csv" in os.listdir("."):
        tasks = pd.read_csv("Tasks.csv")
        tasks['Due Date'] = pd.to_datetime(tasks['Due Date'])
        tasks.to_sql("tasks", conn, if_exists='replace', index=False)