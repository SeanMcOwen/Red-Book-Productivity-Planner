import RedBook
import pandas as pd
import sqlite3
from datetime import datetime


database_name = 'Goals.db'




from datetime import datetime
with sqlite3.connect(database_name) as conn:
    goals, work_log = RedBook.Data.process_goals_SQL(conn)
    expected_progress_table = RedBook.Tables.build_expected_progress_table(goals)
    #expected_work_table = RedBook.Tables.build_expected_work_table(goals)
    
    #expected_progress_table, expected_work_table, expected_work_tables = RedBook.Tables.build_expected_work_tables(goals)
    
    #habits = RedBook.Data.pull_habits_data_SQL(conn)
    #habits_progress = RedBook.Data.pull_habits_log_SQL(conn)
    
    #habits, progress = RedBook.Data.process_habits_SQL(conn)
    #table = RedBook.Tables.build_expected_progress_table_habits(habits)
    #["Daily","Weekly","Monthly","Quarterly","Yearly"]
    #tasks = RedBook.Data.pull_tasks_SQL(conn)

    #RedBook.Data.check_goal_completion(conn, goals)

    
    #Take this group logic and apply it to find a streak for daily, weekly, etc for goals
    
    goal_name = goals['Goal Name'].iloc[0]
    
    
    goal_object = goals.set_index('Goal Name').loc[goal_name, 'Object']
    streak_data, streak = goal_object.compute_streak('Month')

    
    #schedule_name = "Week"
    #date_range = "Overlap"

    #schedule_data, graph_data2 = pull_schedule_data(goals, goal_name, schedule_name, date_range)