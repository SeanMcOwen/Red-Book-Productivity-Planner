from flask import Blueprint,render_template,redirect,url_for, request
from bokeh.embed import server_document
import sqlite3
import RedBook
import pandas as pd

database_name = 'Goals.db'


goals_blueprint = Blueprint('goals',
                              __name__,
                              template_folder='templates')





@goals_blueprint.route("/Goals",methods=['GET', 'POST'])
def goals_page():
    with sqlite3.connect(database_name) as conn:
        if not RedBook.Data.check_table_exists(conn, 'goals'):
            error = "<h3>Please create a goal first.</h3>"
            return render_template("ErrorPage.html", error=error,
                                   template="Flask")
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
        expected_progress_table, expected_work_table, percent_left_table, expected_work_tables = RedBook.Tables.build_expected_work_tables(goals)
        expected_progress_table_today = RedBook.Tables.build_expected_work_tables_today(goals)
    if request.method == 'POST':
        goal_name  = request.values.get('goal')
        goal_names = list(goals['Goal Name'].values)
        goal_names.pop(goal_names.index(goal_name))
        goal_names = [goal_name] + goal_names
        goals = goals.set_index('Goal Name')
        goal_data = {}
        goal_data['Goal Name'] = goal_name
        goal_data['Group'] = goals.loc[goal_name, 'Group']
        goal_data['Start Date'] = goals.loc[goal_name, 'Start Date'].strftime("%m/%d/%Y")
        goal_data['End Date'] = goals.loc[goal_name, 'End Date'].strftime("%m/%d/%Y")
        goal_data['Start Progress'] = goals.loc[goal_name, 'Start Progress']
        goal_data['Current Progress'] = goals.loc[goal_name, 'Object'].current_progress
        goal_data['Goal Progress'] = goals.loc[goal_name, 'Goal Progress']
        goal_data['Percent Complete'] = abs(goal_data['Current Progress'] - goal_data['Start Progress']) / abs(goal_data['Goal Progress'] - goal_data['Start Progress'])
        
        increment_table = pd.concat([x.loc[goal_name] for x in expected_work_tables.values()], axis=1).transpose()
        increment_table.index = list(expected_work_tables.keys())
        
        increment_table2 = pd.concat([x.loc[goal_name] for x in expected_progress_table_today.values()], axis=1).transpose()
        increment_table2.index = list(expected_progress_table_today.keys())
        
        
        current_table = increment_table.copy()
        current_table = current_table.dropna()
        if 'Percent Left' in current_table.columns:
            current_table['Percent Left'] = current_table['Percent Left'] * 100
            current_table = current_table.round(2)
            current_table['Percent Left'] = current_table['Percent Left'].astype(str) +"%"
        increment_table_html = current_table.to_html()
        
        current_table = increment_table2.copy()
        current_table = current_table.dropna()
        if 'Percent Left' in current_table.columns:
            current_table['Percent Left'] = current_table['Percent Left'] * 100
            current_table = current_table.round(2)
            current_table['Percent Left'] = current_table['Percent Left'].astype(str) +"%"
        increment_table_html2 = current_table.to_html()
        
        scheduleScript = server_document('http://localhost:5006/schedules',
                                         arguments={'goal_name': goal_name})
        
        return render_template("Goals.html",goals=goal_names, template="Flask",
                               goal_data=goal_data, increment_table = increment_table_html,
                               increment_table2 = increment_table_html2,
                               scheduleScript=scheduleScript)
        
    return render_template("Goals.html",goals=list(goals['Goal Name'].values), template="Flask")


@goals_blueprint.route("/Habits",methods=['GET', 'POST'])
def habits_page():
    pass

