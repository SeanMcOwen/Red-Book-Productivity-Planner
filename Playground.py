import RedBook
import pandas as pd
import sqlite3
from datetime import datetime


database_name = 'Goals.db'
with sqlite3.connect(database_name) as conn:
    goals, work_log = RedBook.Data.process_goals_SQL(conn)
    #expected_progress_table = RedBook.Tables.build_expected_progress_table(goals)
    #expected_work_table = RedBook.Tables.build_expected_work_table(goals)
    
    #expected_progress_table, expected_work_table, expected_work_tables = RedBook.Tables.build_expected_work_tables(goals)
    
    

schedule_name = 'Week'

group = goals[goals['Group'] == 'Quant Education']
#group_schedules = 



group = RedBook.Classes.Group(group)
data = group.build_group_schedule('Week', data_type = 'Completion')
print(data)

"""
goal_name = 'Red Book'
key = 'Week'
goal= goals.set_index('Goal Name').loc[goal_name, 'Object']
schedule = goal.compute_PIT_increments(key, expand_dates=False)

goal = goals.set_index("Goal Name").loc['Red Book', 'Object']

schedule = goal.compute_PIT_increments('Today', expand_dates=True)

assert False
schedules = temp.compute_PIT_schedules('Week', 'Goal Period')
#pd.DataFrame([[x.iloc[-1]-x.iloc[0],
#  x.index[1],
#  x.index[-1]] for x in schedules], columns=['Increment', 'Start Date', 'End Date'])

#Get the expected increments

import matplotlib.pyplot as plt
overlap=True
for s in schedules:
    if overlap:
        s = s.loc[:temp.progress_log.index[-1]]
    s.plot(kind='line')
temp.progress_log.plot(kind='line')
plt.show()
"""
