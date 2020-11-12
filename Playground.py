import RedBook
import pandas as pd
import sqlite3
from datetime import datetime


database_name = 'Goals.db'




from datetime import datetime
with sqlite3.connect(database_name) as conn:
    
    #goals, work_log = RedBook.Data.process_goals_SQL(conn)
    #expected_progress_table, expected_work_table, percent_left_table, expected_work_tables = RedBook.Tables.build_expected_work_tables(goals)
    #RedBook.Data.filter_increment_hiding(goals, expected_work_tables)
    #print(RedBook.Data.check_table_exists(conn, 'groups'))
    #tables 
    #goals, work_log = RedBook.Data.process_goals_SQL(conn)
    #expected_progress_table = RedBook.Tables.build_expected_progress_table(goals)
    #expected_work_table = RedBook.Tables.build_expected_work_table(goals)
    
    #expected_progress_table, expected_work_table, expected_work_tables = RedBook.Tables.build_expected_work_tables(goals)
    
    #habits = RedBook.Data.pull_habits_data_SQL(conn)
    #habits_progress = RedBook.Data.pull_habits_log_SQL(conn)
    
    #habits, progress = RedBook.Data.process_habits_SQL(conn)
    #table = RedBook.Tables.build_expected_progress_table_habits(habits)
    #["Daily","Weekly","Monthly","Quarterly","Yearly"]
    #tasks = RedBook.Data.pull_tasks_SQL(conn)

    #RedBook.Data.check_goal_completion(conn, goals)
    tasks = RedBook.Data.pull_tasks_SQL(conn)
    