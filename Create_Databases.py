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
