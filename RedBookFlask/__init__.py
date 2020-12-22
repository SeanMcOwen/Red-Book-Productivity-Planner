from flask import Flask,request, render_template
import sqlite3
import pandas as pd
from Create_Databases import excel_to_db
import RedBook, RedBookBokeh

from threading import Thread
from tornado.ioloop import IOLoop
from bokeh.embed import server_document

from bokeh.server.server import Server
import os

database_name = 'Goals.db'
"""if 'Goals.csv' not in os.listdir('/'):
    cols = ['Goal #', 'Goal Name', 'Group', 'Start Progress', 'Goal Progress',
       'Start Date', 'End Date', 'Progress Type', 'Completed', 'Units',
       'Today', 'Week', 'Month', 'Quarter', 'Year', 'Historical']
    pd.DataFrame([], columns=cols).to_csv("Goals.csv")"""
with sqlite3.connect(database_name) as conn:
    excel_to_db(conn)
app = Flask(__name__)


from RedBookFlask.Schedules.views import schedules_blueprint
from RedBookFlask.Increments.views import increments_blueprint
from RedBookFlask.Goals.views import goals_blueprint
from RedBookFlask.Groups.views import groups_blueprint
from RedBookFlask.Create.views import create_blueprint
from RedBookFlask.Playground.views import playground_blueprint
from RedBookFlask.Habits.views import habits_blueprint
from RedBookFlask.Rules.views import rules_blueprint

app.register_blueprint(schedules_blueprint,url_prefix="/Schedules")
app.register_blueprint(increments_blueprint,url_prefix="/Increments")
app.register_blueprint(goals_blueprint,url_prefix="/Goals")
app.register_blueprint(groups_blueprint,url_prefix="/Groups")
app.register_blueprint(create_blueprint,url_prefix="/Create")
app.register_blueprint(playground_blueprint,url_prefix="/Playground")
app.register_blueprint(habits_blueprint,url_prefix="/Habits")
app.register_blueprint(rules_blueprint,url_prefix="/Rules")


app.config['SECRET_KEY'] = 'TEST'


@app.route("/",methods=['GET', 'POST'])
def main():
    with sqlite3.connect(database_name) as conn:
        try:
            goals, work_log = RedBook.Data.process_goals_SQL(conn)
            expected_progress_table, expected_work_table, percent_left_table, expected_work_tables = RedBook.Tables.build_expected_work_tables(goals)
            expected_progress_table_today = RedBook.Tables.build_expected_work_tables_today(goals)
            RedBook.Data.filter_increment_hiding(goals,expected_work_tables)
        except:
            goals = None
            
        try:
            habits, progress = RedBook.Data.process_habits_SQL(conn)
            table = RedBook.Tables.build_expected_progress_table_habits(habits)
        except:
            habits = None
            
        try:
            tasks = RedBook.Data.pull_tasks_SQL(conn)
        except:
            tasks = None
    
    tables_d = {}
    for label1, label2 in zip(["Today","Week","Month","Quarter","Year"],["Daily","Weekly","Monthly","Quarterly","Yearly"]):
        tables = ""
        if goals is not None:
            for x in [label1]:
                tables += "<h3>Goals</h3>"
                current_table = expected_work_tables[x].copy()
                current_table = current_table.dropna()
                if 'Percent Left' in current_table.columns:
                    current_table['Percent Left'] = current_table['Percent Left'] * 100
                    current_table = current_table.round(2)
                    current_table['Percent Left'] = current_table['Percent Left'].astype(str) +"%"
                tables += current_table.to_html()
                tables += "<br>"
        
        if habits is not None:
            for col in [label2]:
                temp = table[(table['Frequency'] == col) & (table['Progress Left'] > 0)]
                if len(temp) > 0:
                    tables += "<h3>Habits</h3>"
                    tables += temp.to_html(index=False)
                    tables += "<br>"
                else:
                    continue
        
        if tasks is not None:
            for col in [label1]:
                temp = tasks[tasks[col]][['Task Name', 'Due Date']]
                if len(temp) > 0:
                    tables += "<h3>Tasks</h3>"
                    tables += temp.to_html(index=False)
                    tables += "<br>"
                else:
                    continue
        tables_d[label1] = tables
    return render_template("Home.html", template="Flask", tables=tables_d)

