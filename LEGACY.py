from flask import Flask,request, render_template
import sqlite3
import pandas as pd
from Create_Databases import excel_to_db
import RedBook, RedBookBokeh

from threading import Thread
from tornado.ioloop import IOLoop
from bokeh.embed import server_document

from bokeh.server.server import Server

database_name = 'Goals.db'
with sqlite3.connect(database_name) as conn:
    excel_to_db(conn)
    



app = Flask(__name__)
@app.route("/",methods=['GET', 'POST'])
def main():
    return render_template("Home.html", template="Flask")



@app.route("/Goals",methods=['GET', 'POST'])
def goals_page():
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
        expected_progress_table = RedBook.Tables.build_expected_progress_table(goals)
        expected_work_table = RedBook.Tables.build_expected_work_table(goals)
        
    return expected_progress_table.fillna("").to_html() + expected_work_table.fillna("").to_html()

@app.route("/Increments",methods=['GET', 'POST'])
def increments_page():
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
        goals = goals[goals['Group'] != 'Fitness']
        expected_progress_table, expected_work_table, percent_left_table, expected_work_tables = RedBook.Tables.build_expected_work_tables(goals)
        expected_progress_table_today = RedBook.Tables.build_expected_work_tables_today(goals)
    tables = ""
    for x in expected_work_tables.keys():
        tables += "<h3>"+x+"</h3>"
        tables += expected_work_tables[x].dropna().to_html()
        tables += "<br>"
        
    tables2 = ""
    for x in expected_progress_table_today.keys():
        tables2 += "<h3>"+x+"</h3>"
        tables2 += expected_progress_table_today[x].dropna().to_html()
        tables2 += "<br>"
    return render_template("Increments.html", tables1=tables, tables2=tables2, template="Flask")

@app.route("/Schedules")
def schedules_page():
    script = server_document('http://localhost:5006/schedules')
    return render_template("embed.html", script=script, template="Flask")


@app.route("/Daily Increments Tracker")
def daily_increments_page():
    script = server_document('http://localhost:5006/dailyincrements')
    return render_template("embed.html", script=script, template="Flask")
   
@app.route("/EffectiveDates")
def effective_dates_page():
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
        goals = goals[goals['Group'] != 'Fitness']
    effective_dates_table = RedBook.Tables.build_effective_date_table(goals)
    tables = ""
    tables += "<h3>Effective Dates</h3>"
    tables += effective_dates_table.to_html()
    tables += "<br>"
    return tables

@app.route("/SchedulesPIT")
def schedules_PIT_page():
    script = server_document('http://localhost:5006/schedulesPIT')
    return render_template("embed.html", script=script, template="Flask")


@app.route("/calendar")
def calendar_page():
    script = server_document('http://localhost:5006/calendar')
    return render_template("embed.html", script=script, template="Flask")

def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    server = Server({'/schedules': RedBookBokeh.schedules,
                     '/dailyincrements': RedBookBokeh.dailyIncrementsTracker,
                     '/schedulesPIT': RedBookBokeh.schedules_PIT,
                     '/calendar': RedBookBokeh.calendar_view}, io_loop=IOLoop(), allow_websocket_origin=["localhost:8000"])
    server.start()
    server.io_loop.start()



if __name__ == "__main__":
    Thread(target=bk_worker).start()
    app.run(debug=False, port=8000)