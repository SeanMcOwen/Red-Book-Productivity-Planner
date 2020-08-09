import sqlite3
import pandas as pd

def excel_to_db(conn):

    #Create unique index for database
    goals = pd.read_csv("Goals.csv")
    progress = pd.read_csv("project_log.csv", index_col=0)
    progress.index = pd.to_datetime(progress.index)
    progress = progress.stack().reset_index()
    progress.columns = ['Date', 'Goal Name', 'Value']
    #Dual index of date and goal
    goals.to_sql("goals", conn, if_exists='replace', index=False)
    progress.to_sql("progress", conn, if_exists='replace', index=False)
