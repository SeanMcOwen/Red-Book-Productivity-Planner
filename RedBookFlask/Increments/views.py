from flask import Blueprint,render_template,redirect,url_for
from bokeh.embed import server_document
import sqlite3
import RedBook

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




