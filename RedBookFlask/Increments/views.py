from flask import Blueprint,render_template,redirect,url_for
from bokeh.embed import server_document
import sqlite3
import RedBook
from flask_table import Table, Col

database_name = 'Goals.db'


increments_blueprint = Blueprint('increments',
                              __name__,
                              template_folder='templates')





@increments_blueprint.route("/Increments",methods=['GET', 'POST'])
def increments_page():
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
        expected_progress_table, expected_work_table, percent_left_table, expected_work_tables = RedBook.Tables.build_expected_work_tables(goals)
        expected_progress_table_today = RedBook.Tables.build_expected_work_tables_today(goals)
    RedBook.Data.filter_increment_hiding(goals,expected_work_tables)
    RedBook.Data.filter_increment_hiding(goals,expected_progress_table_today)
    tables = ""
    for x in expected_work_tables.keys():
        tables += "<h3>"+x+"</h3>"
        current_table = expected_work_tables[x].copy()
        current_table = current_table.dropna()
        if 'Percent Left' in current_table.columns:
            current_table['Percent Left'] = current_table['Percent Left'] * 100
            current_table = current_table.round(2)
            current_table['Percent Left'] = current_table['Percent Left'].astype(str) +"%"
        tables += current_table.to_html()
        tables += "<br>"
        
    tables2 = ""
    for x in expected_progress_table_today.keys():
        tables2 += "<h3>"+x+"</h3>"
        current_table = expected_progress_table_today[x].copy()
        current_table = current_table.dropna()
        current_table = current_table.round(2)
        tables2 += current_table.to_html()
        tables2 += "<br>"
    return render_template("Increments.html", tables1=tables, tables2=tables2, template="Flask")




@increments_blueprint.route("/Daily Increments Tracker")
def daily_increments_page():
    script = server_document('http://localhost:5006/dailyincrements')
    return render_template("embed.html", script=script, template="Flask")



@increments_blueprint.route("/Progress Bars")
def progress_bars_page():
    script = server_document('http://localhost:5006/progressbars')
    return render_template("embed.html", script=script, template="Flask")

@increments_blueprint.route("/Habits Increments",methods=['GET', 'POST'])
def habits_increments_page():
    with sqlite3.connect(database_name) as conn:
        habits, progress = RedBook.Data.process_habits_SQL(conn)
        table = RedBook.Tables.build_expected_progress_table_habits(habits)
    
    tables = ""
    for col in ["Daily","Weekly","Monthly","Quarterly","Yearly"]:
        temp = table[(table['Frequency'] == col) & (table['Progress Left'] > 0)]
        if len(temp) > 0:
            tables += "<h3>"+col+"</h3>"
            tables += temp.to_html(index=False)
            tables += "<br>"
        else:
            continue
        
    return render_template("HabitsIncrements.html", tables1=tables, template="Flask")


@increments_blueprint.route("/Tasks Increments",methods=['GET', 'POST'])
def task_increments_page():
    with sqlite3.connect(database_name) as conn:
        tasks = RedBook.Data.pull_tasks_SQL(conn)
    
    tables = ""
    for col in ["Today","Week","Month","Quarter","Year"]:
        temp = tasks[tasks[col]][['Task Name', 'Due Date']]
        if len(temp) > 0:
            tables += "<h3>"+col+"</h3>"
            tables += temp.to_html(index=False)
            tables += "<br>"
        else:
            continue
    temp = tasks[['Task Name', 'Due Date']]
    tables += "<h3>All Tasks</h3>"
    tables += temp.to_html(index=False)
    tables += "<br>"
    
    task_table = TaskTable([[x[0], x[1]] for x in temp.values])
        
    return render_template("TaskIncrements.html", tables1=tables, template="Flask")


class TaskTable(Table):
    task_name = Col('Task Name')
    due_date = Col('Due Date')
    
class TaskItem(object):
    def __init__(self, task_name, due_date):
        self.task_name = task_name
        self.due_date = due_date
